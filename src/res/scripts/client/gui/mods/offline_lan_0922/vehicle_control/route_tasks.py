"""Ordered travel tasks observing the shared native combat movement owner."""
from __future__ import division
from gui.mods.offline_lan_0922.vehicle_control.strategy_compat import text as str, round_py3 as round
import copy
import json
import math
from gui.mods.offline_lan_0922.vehicle_control import strategy_compat
import os
import zipfile

from gui.mods.offline_lan_0922 import bot_tactics
from gui.mods.offline_lan_0922 import route_network
from gui.mods.offline_lan_0922 import spg_positions
from gui.mods.offline_lan_0922.ai.driver import WAYPOINT_ARRIVAL_RADIUS
from gui.mods.offline_lan_0922.vehicle_control.route_recovery import MIN_ROUTE_AFFINITY


DEFENSE_SEARCH_STALL_SECONDS = 6.0
DEFENSE_SEARCH_DIRECTIONS = (('x+', 1, 0), ('x-', -1, 0), ('z+', 0, 1), ('z-', 0, -1))
DEFENSE_SEARCH_ADJUSTMENTS = {
    ('04_himmelsdorf', 1, 'z-'): (2., -270.),
    ('86_himmelsdorf_winter', 1, 'z-'): (2., -270.),
    ('112_eiffel_tower_ctf', 2, 'z+'): (338., 6.),
    ('31_airfield', 2, 'x+'): (-306., -178.),
    ('31_airfield', 2, 'z-'): (-318., -190.),
    ('63_tundra', 1, 'x-'): (58., -166.),
    ('63_tundra', 2, 'z-'): (-70., 122.),
    ('95_lost_city', 1, 'x-'): (266., -94.),
    ('95_lost_city', 2, 'x+'): (-266., 94.),
}


def point(value):
    if isinstance(value, dict):return dict((k, float(value.get(k, 0))) for k in ('x', 'y', 'z'))
    return dict(x=float(value[0]), y=0., z=float(value[1]))


def distance(a, b):
    return math.hypot(a['x']-b['x'], a['z']-b['z'])


class RouteTasksMixin:
    @staticmethod
    def _combat_movement_task(bot):
        """Read the native owner's suspended route, without deciding combat."""
        if not isinstance(bot, dict) or bot.get('empty_ammo'):
            return None
        receipt = (bot.get('state') or {}).get('_combat_movement_owner')
        if not isinstance(receipt, dict) or receipt.get('owned') is not True:
            return None
        task = receipt.get('task_order')
        if not isinstance(task, dict) or not isinstance(task.get('move_position'), dict):
            return None
        return task

    def _task_combat(self, order, bot=None):
        mode=order.get('combat_mode')
        explicit = bool(order.get('target_id') is not None and mode in (
            'engage', 'advance_contact'))
        # A new explicit task is evaluated by its existing task owner. A
        # receipt from the previous callback must not cancel that command.
        combat_command = order.get('team_command') in (
            None, 'ATTACK', 'ATTACKENEMY', 'SUPPORTMEWITHFIRE')
        ordinary_travel = (mode in ('route', 'advance', 'advance_contact', 'engage',
            'team_attack', 'route_transfer', 'parking_approach') or
            mode == 'base_capture' and order.get('throttle_override') != 0.)
        return bool(explicit or (combat_command and ordinary_travel and
            order.get('defense_base_id') is None and self._combat_movement_task(bot) is not None))

    def _task_pause_route(self, order, bot, now):
        """Pause the existing route-attempt clock while native combat moves."""
        progress = self._wreck_route_progress.get(bot['id'])
        if progress is not None:
            progress.setdefault('paused_at', now)
            progress.setdefault('pause_pose', point(bot['state']))
            recovery = self._route_recoveries.get(bot['id'])
            order['route_attempt'] = dict(route_id=progress['key'][0],
                route_index=progress['key'][1], action='pause_combat_owner',
                elapsed=round(progress['paused_at']-progress['since'], 3),
                phase=recovery['phase'] if recovery else None)

    def _task_init(self):
        self._travel_tasks = {}
        self._previous_combat = set()
        self._previous_player = {}
        self._travel_graph_cache = {}
        self._empty_task_reports = 0

    def _task_route(self, bot):
        return (self._route_assignments.get(bot['id']) or {}).get('route') or bot.get('route') or {}

    def _task_family(self,route,team):
        config=bot_tactics.route_config(self.tactics,self.tactics_map,route.get('id'),team)
        if config:
            return ('user_'+config.get('family',config['id'])) if not config.get('default') else config['source_id']
        return str(route.get('_route_family') or route.get('_editor_source') or route.get('id') or '')

    def _task_class_route(self,route,bot,catalog):
        family=self._task_family(route,bot['team']);tag=bot['profile'].get('class_tag')
        def applicable(candidate):
            config=bot_tactics.route_config(self.tactics,self.tactics_map,candidate.get('id'),bot['team'])
            return (self._task_family(candidate,bot['team'])==family and
                (not config or bot_tactics.matches(config,bot)) and
                (candidate.get('class_weights') or {}).get(tag,1.)>=MIN_ROUTE_AFFINITY)
        choices=[candidate for candidate in catalog.values() if applicable(candidate)]
        if choices:return min(choices,key=lambda r:(r['id']!=route['id'],r['id']))
        settings=bot_tactics.map_settings(self.tactics,self.tactics_map)
        rows=[r for r in settings.get('default_routes',()) if r['team']==bot['team'] and r['id']==family and not r.get('disabled') and r.get('class_tag','all') in (tag,'all')]
        if rows:
            from gui.mods.offline_lan_0922 import bot_tactics_runtime
            graph=self._task_graph()
            rows=[row for row in rows if graph is not None and bot_tactics_runtime.validate_route(graph,row) is None]
        if rows:
            row=min(rows,key=lambda r:r.get('class_tag','all')!=tag)
            return dict(id=bot_tactics.default_route_id(row),capacity=15,
                class_weights={tag:1.},waypoints=[point(p) for p in row['points']])
        return None

    def _task_graph(self):
        name = self.tactics_map
        if name not in self._travel_graph_cache:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 8)))
            try:
                path = os.path.join(root, 'navgraphs', name+'.json')
                if os.path.isfile(path):
                    with strategy_compat.open_text(path) as stream:raw = json.load(stream)
                else:
                    archive = os.path.join(root, '..', '..', 'client', '0.9.22.zip')
                    with zipfile.ZipFile(archive) as packed:
                        raw = json.loads(packed.read('mods/configs/offline_lan_0922/navgraphs/'+name+'.json'))
                self._travel_graph_cache[name] = spg_positions._Graph(raw, bot_tactics.MAPS[name]['bounds'])
            except (IOError, OSError, ValueError, KeyError, strategy_compat.BadZipFile):
                self._travel_graph_cache[name] = None
        return self._travel_graph_cache[name]

    def _task_rejoin(self, bot):
        """Nearest reachable point by directed graph travel, only on handoff."""
        route = self._task_route(bot)
        points = route.get('waypoints') or []
        graph = self._task_graph()
        if not points or graph is None:return
        pose = point(bot['state'])
        index=route_network.reachable_join(graph,(pose['x'],pose['y'],pose['z']),points)
        if index is not None:
            self._cycle_drop_parking(bot)
            state=self._route_states.setdefault(bot['id'],{})
            state.update(route_id=route['id'],index=index,join_index=index,join_anchor=pose)
            state.pop('arrival_previous_pose',None)

    def _task_position(self, bot, now):
        task = self._travel_tasks[bot['id']]
        goal = task['points'][task['index']]
        return task['route_id'], task['source_index'], goal, point(bot['state']), True

    def _task_begin(self, bot, kind, base=None, target_route=None, now=0.):
        route = self._task_route(bot)
        source = route.get('waypoints') or []
        state = self._route_states.get(bot['id']) or {}
        index = max(0, min(int(state.get('index', 0))-1, len(source)-1))
        config = bot_tactics.route_config(self.tactics, self.tactics_map, route.get('id'), bot['team'],source)
        junction = -1
        if config and config.get('defense'):
            junction = route_network.nodes(config).index(config['defense']['junction'])
        end = junction if kind in ('defense', 'guard') and index >= junction >= 0 else 0
        # Unconfigured artillery legitimately has no ordinary route. It still
        # receives a base target below, using the existing local navigation.
        path = [point(source[i]) for i in range(index, end-1, -1)] if source else []
        if kind in ('defense', 'guard'):
            if end == junction and config:
                path += [point(p) for p in config['defense']['points'][1:]]
            path.append(point(base['point']))
        elif target_route:
            path.append(point(target_route['waypoints'][0]))
        if not path:path = [point(bot['state'])]
        if (not source and os.environ.get('WOT_OFFLINE_DIAGNOSTICS') == '1'
                and self._empty_task_reports < 64):
            self._empty_task_reports += 1
            try:
                print('[Offline LAN 0.9.22] ROUTE TASK EMPTY SOURCE '+json.dumps(dict(
                    round=self._round_id, map=self.tactics_map, bot=bot['id'], team=bot['team'],
                    class_tag=bot['profile'].get('class_tag'), kind=kind,
                    route_id=route.get('id'), source_count=0, points=path,
                    base_id=(base or {}).get('base_id'), policy='existing_target_navigation'),sort_keys=True))
            except Exception:
                pass  # Diagnostic output must not prevent a valid task.
        task = dict(kind=kind, route_id=str(route.get('id') or ''), route=route,
            source_index=index, points=path, index=0, since=now, best=float('inf'),
            target_route=target_route, until=now+180., base=copy.deepcopy(base), root_index=max(0,index-end), last_source=index,
            original_parking=copy.deepcopy(bot.get('spg_initial')))
        self._travel_tasks[bot['id']] = task
        if kind in ('defense', 'guard'):
            self._route_recoveries.pop(bot['id'], None)
            self._wreck_route_progress.pop(bot['id'], None)
        self._cycle_drop_parking(bot)
        return task

    @staticmethod
    def _inside_defended_base(bot, base):
        pose = bot['state']
        return bool(pose.get('world_pose') and distance(point(pose), base['point']) <= base['radius'])

    def _defense_search_points(self, base, team):
        centre = base['point']
        half_radius = base['radius'] * .5
        graph = self._task_graph()
        points = {}
        for direction, dx, dz in DEFENSE_SEARCH_DIRECTIONS:
            x, z = DEFENSE_SEARCH_ADJUSTMENTS.get((self.tactics_map, team, direction),
                (centre['x'] + dx * half_radius, centre['z'] + dz * half_radius))
            cell = graph.closest((x, 0., z)) if graph is not None else None
            y = graph.point(cell)[1] if cell is not None else centre['y']
            points[direction] = dict(x=x, y=y, z=z)
        return points

    def _defense_search_report(self, bot, task, now, action, **details):
        search = task['search']
        event = dict(at=now, action=action, bot=bot['id'], team=bot['team'],
            base=task['base']['base_id'], sweep=search['sweep'],
            direction=search['direction'], **details)
        if os.environ.get('WOT_OFFLINE_DIAGNOSTICS') == '1':
            try:
                print('[Offline LAN 0.9.22] BOT DEFENSE SEARCH ' + json.dumps(event, sort_keys=True))
            except (ValueError, IOError):
                pass
        return event

    def _task_publish_defense_inside(self, order, bot, task, now):
        base = task['base']
        pose = point(bot['state'])
        artillery_engagement = (bot['profile'].get('class_tag') == 'SPG' and
            order.get('target_id') is not None and order.get('fire_allowed'))
        order.update(defense_base_id=str(base['base_id']), defense_arrived=True,
            combat_mode='engage' if artillery_engagement else 'route',
            move_position=pose, throttle_override=0., route_join=False,
            parking_phase=None, parking_slot=None)
        if not task.get('search_active'):
            task.pop('search', None)
            if order.get('target_id') is not None:
                order['combat_mode'] = 'engage'
            return

        search = task.get('search')
        if search is None:
            search = task['search'] = dict(points=self._defense_search_points(base, bot['team']),
                sweep=1, attempted={}, direction=None, paused_at=None)
        if artillery_engagement or self._combat_movement_task(bot) is not None:
            if search['paused_at'] is None:
                search['paused_at'] = now
            evidence = order.get('tactical_evidence')
            if evidence is not None:
                evidence['defense_search'] = dict(action='combat_priority',
                    sweep=search['sweep'], direction=search['direction'])
            return

        direction = search['direction']
        if direction is not None:
            if search['paused_at'] is not None:
                search['since'] += now - search['paused_at']
            remaining = distance(pose, search['points'][direction])
            if remaining < search['best'] - .5:
                search.update(best=remaining, since=now)
            elapsed = now - search['since']
            outcome = None
            if remaining <= WAYPOINT_ARRIVAL_RADIUS:
                outcome = 'arrived'
            elif elapsed >= DEFENSE_SEARCH_STALL_SECONDS:
                outcome = 'blocked_timeout'
            if outcome is not None:
                search['attempted'][direction] = outcome
                self._defense_search_report(bot, task, now, outcome,
                    elapsed=round(elapsed, 3), distance=round(remaining, 3),
                    arrived=sum(value == 'arrived' for value in search['attempted'].values()))
                direction = None
        search['paused_at'] = None

        points = search['points']
        if direction is None:
            if len(search['attempted']) == len(points):
                search['sweep'] += 1
                search['attempted'].clear()
            occupied = set(other['search']['direction'] for other in self._travel_tasks.values()
                if other is not task and other.get('search') is not None and
                   other['search']['paused_at'] is None and
                   other['base']['base_id'] == base['base_id'])
            direction = min((key for key in points if key not in search['attempted']),
                key=lambda key: (key in occupied, distance(pose, points[key]), key))
            search.update(direction=direction, since=now, best=distance(pose, points[direction]))
            self._defense_search_report(bot, task, now, 'attempt', position=pose, goal=points[direction])

        goal = points[direction]
        order.update(move_position=dict(goal), face_position=order.get('face_position') if
            order.get('target_id') is not None else dict(goal), route_anchor=pose, route_join=True,
            arrival_radius=WAYPOINT_ARRIVAL_RADIUS, throttle_override=None,
            travel_task=dict(kind='defense', phase='search', direction=direction, sweep=search['sweep']))
        evidence = order.get('tactical_evidence')
        if evidence is not None:
            evidence['defense_search'] = dict(action='moving', direction=direction,
                sweep=search['sweep'], attempted=dict(search['attempted']))

    def _task_publish(self, order, bot, task, now):
        base = task.get('base')
        if task['kind'] == 'defense' and base:
            inside = self._inside_defended_base(bot, base)
            if inside:
                task['arrived'] = True
                self._task_publish_defense_inside(order, bot, task, now)
                return
            search = task.get('search')
            if search is not None and search['paused_at'] is None:
                search['paused_at'] = now
        else:
            inside = base and self._inside_base(bot,base)
            if inside:
                task['arrived'] = True
        if task['kind'] == 'pressure' and now >= task['until']:
            self._travel_tasks.pop(bot['id'], None)
            state=self._route_states.setdefault(bot['id'],{})
            state.update(route_id=task['route_id'],index=task['last_source'],join_index=task['last_source'],join_anchor=point(bot['state']))
            move=self._route(bot,now)[2]
            order.update(route_id=task['route_id'],route_index=state['index'],move_position=move,combat_mode='route',throttle_override=None)
            return
        if task.get('arrived'):
            order.update(move_position=point(bot['state']) if inside else point(base['point']), throttle_override=0. if inside else None,
                         combat_mode='engage' if inside and order.get('target_id') is not None else 'base_defense' if task['kind']=='defense' else 'team_guard')
            return
        goal = task['points'][task['index']]
        d = distance(point(bot['state']), goal)
        if d < task['best']-.5:
            task.update(best=d, since=now)
        previous_index=task['index']
        reached = d <= bot_tactics.ROUTE_ARRIVAL_RADIUS
        if reached:
            task['failures']=0
            if task['index']<=task['root_index']:task['last_source']=max(0,task['source_index']-task['index'])
            task['index'] += 1
            task.update(best=float('inf'), since=now)
        elif now-task['since'] >= 20.:
            # A return gate gets local motion recovery first, then one skip.
            # Defense owns the explicit direct-base fallback after two failures.
            failures = task.get('failures', 0)+1
            task.update(failures=failures, best=float('inf'), since=now)
            if task['kind'] in ('defense', 'guard') and failures >= 2:
                task['points'] = [point(base['point'])];task['index'] = 0
            elif task['index'] < len(task['points'])-1 and not (task['kind']=='pressure' and task['index']>=task['root_index']):task['index'] += 1
        if task['index'] >= len(task['points']):
            if task['kind'] == 'pressure':
                route = task['target_route']
                self._route_assignments[bot['id']] = dict(route=route, until=0., ordered_task=True)
                self._route_states[bot['id']] = dict(route_id=route['id'], index=0)
                self._route_history.setdefault(bot['id'], {}).pop(route['id'], None)
                self._travel_tasks.pop(bot['id'], None)
                move = self._route(bot, now)[2]
                order.update(route_id=route['id'], route_index=0, move_position=move, combat_mode='route', throttle_override=None)
                return
            task['index'] = len(task['points'])-1
        goal = task['points'][task['index']]
        if task['index']!=previous_index:task['best']=distance(point(bot['state']),goal)
        order.update(move_position=dict(goal), route_anchor=point(bot['state']), route_join=True,
            throttle_override=None, parking_phase=None, parking_slot=None,
            combat_mode='base_defense' if task['kind']=='defense' else
                        'team_back_to_base' if task['kind']=='guard' else 'route_transfer')
        if task['kind']=='defense':order['defense_base_id'] = str(base['base_id'])
        if task['kind']=='pressure':order.update(target_id=None, fire_allowed=False)
        order['travel_task'] = dict(kind=task['kind'], index=task['index'], route_id=task['route_id'])

    def _task_capture_handoff(self,order,bot,target):
        if (target is None or bot['id'] in self._travel_tasks or bot['id'] in self._route_recoveries or
                order.get('team_command') or order.get('target_id') is not None or
                bot['profile'].get('class_tag')=='SPG' or
                order.get('combat_mode') not in ('route','advance','base_screen')):return
        route=self._task_route(bot)
        authored=bot_tactics.route_config(self.tactics,self.tactics_map,route.get('id'),bot['team'],route.get('waypoints'))
        state=self._route_states.get(bot['id']) or {}
        if (authored is None or state.get('holding') or state.get('parking_phase') in ('approach','waiting','queue')):return
        if self._inside_base(bot,target) or state.get('index')==len(route.get('waypoints',()))-1:
            self._apply_base_capture_order(order,bot,target)

    def _task_apply(self, order, bot, now, defense_record=None, player_order=None, defense=None):
        if bot.get('empty_ammo'):return
        actor = bot['id']
        combat = self._task_combat(order, bot)
        previous=self._previous_player.get(actor)
        command_id=(player_order or {}).get('command_id')
        if previous and previous['id']!=command_id:
            self._previous_player.pop(actor,None)
            if not combat and actor not in self._route_recoveries and actor not in self._travel_tasks:
                self._task_rejoin(bot)
                if not player_order:
                    identity,index,move,anchor,join=self._route(bot,now)
                    order.update(route_id=identity,route_index=index,move_position=move,route_anchor=anchor,route_join=join)
        if player_order:
            if not previous or previous['id']!=command_id:
                previous=dict(id=command_id,command=player_order.get('command'),goal=copy.deepcopy(order.get('move_position')))
                self._previous_player[actor]=previous
        task = self._travel_tasks.get(actor)
        released=False
        combat = self._task_combat(order, bot)
        if defense_record is not None:
            if (task is None or task['kind'] != 'defense' or
                    task['base']['base_id'] != defense_record['base_id']):
                task = self._task_begin(bot, 'defense', defense_record, now=now)
            task['search_active'] = defense_record.get('search_active', False)
        elif task and task['kind'] == 'defense':
            self._travel_tasks.pop(actor, None);self._task_rejoin(bot);task = None;released=True
        if task is None and player_order and player_order.get('command') == 'BACKTOBASE' and not combat:
            bases = self._defense_points((defense or {}).get('capture_bases'), bot['team'])
            if bases:
                base = min(bases, key=lambda b:distance(point(bot['state']), b['point']))
                task = self._task_begin(bot, 'guard', dict(base_id=base['id'], **base), now=now)
        if task and task['kind']=='guard' and (not player_order or player_order.get('command')!='BACKTOBASE' or combat):
            self._travel_tasks.pop(actor, None);self._task_rejoin(bot);task = None;released=True
        if combat and (not task or task['kind']!='defense'):
            self._previous_combat.add(actor)
            if task:task['paused_at'] = task.get('paused_at', now)
            return
        if actor in self._previous_combat:
            self._previous_combat.discard(actor)
            if not task and actor not in self._route_recoveries:
                self._task_rejoin(bot)
                if not player_order:
                    identity,index,move,anchor,join=self._route(bot,now)
                    order.update(route_id=identity,route_index=index,move_position=move,route_anchor=anchor,route_join=join)
        if released and not task and not player_order and order.get('combat_mode') in ('route','advance','base_screen'):
            identity,index,move,anchor,join=self._route(bot,now)
            order.update(route_id=identity,route_index=index,move_position=move,route_anchor=anchor,route_join=join)
        if task:
            if 'paused_at' in task:
                pause = now-task.pop('paused_at');task['since'] += pause
            self._task_publish(order, bot, task, now)
