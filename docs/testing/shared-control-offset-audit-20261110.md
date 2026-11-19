# PR119 control-offset correction — November 10, 2026

## Current follow-up — November 19, 2026, garage/rear-turn/retirement

Implementation is under verification; no native acceptance or new delivery is
claimed yet. The original PR119 remains open and unmerged. Original navigation,
route data, search and driving owners have no changes in this follow-up.

- CMD 119 now implements the pinned buy-and-equip contract: purchase only
  missing exterior copies, transfer inventory and persist atomically.
- Shared school coefficients restore free .2/.2, credits .1/.1 and gold 0/0
  base/cross-class losses; the exact client still calculates role levels and
  unused XP. Historical evidence/confidence is in COMPATIBILITY_REVIEW.md.
- Lineup and save vehicle filters share full Chinese/English class labels.
- Hydraulic angle inversion reads both actual edge responses; a rear ray no
  longer assumes the nose-up pitch response has the forward sign.
- Endpoint aim and full turn proof use the same continuous support history.
  Checked prefixes resume at the first unfinished slice. Existing support,
  peer, native collision, boundary and first-trigger checks remain active.
- Offline cleanup precedes stock game.fini. Custom muted model references
  retire at stock appearance destruction; ownership hooks remain through
  late stock teardown. A retired chat protocol cannot receive new close events.
- Unresolved Bot command/turn substage timings and model-owner identities are
  recorded only through the checked detailed-diagnostics entrance.

Initial verification: 36 player files, 29 shared-control files (engine-free
Windows reference), 49 launcher files, plus focused garage, shutdown and radio
checks pass. Full reference validation, new-source Windows packaging and exact
client acceptance are in progress. Earlier direct Windows-host shared checks
failed because the x64 test interpreter cannot load the shipping x86 client
extension; no assertion was weakened and those failures are not native passes.

## Previous handoff — November 19, 2026

Runtime/code revision: `bf27cda927b82f962ee0a50846371edcadea0003`, build
`local-pr119-bf27cda9`. This adds checked-only world/wreck/lane-refusal and unsettled-motion
evidence to the native-tested hydraulic correction `97cee192`. Local branch
`fix/pr119-stable-engagement` updates the original PR119 head branch
`fix/elite-premium-ammo-reviewed-guns`; it is not `origin/main`. Keep PR119 open
and unmerged. No tag or release is authorized. Review ZIP:
`C:/Users/USER/Downloads/wot_PR119_bf27cda9_Windows_2026-11-19.zip`.
Its nested client ZIP is byte-identical to the native test payload; the clean
delivery stage and outer ZIP inventory/integrity checks pass.

Confirmed corrections in this follow-up:

- Actual-barrel artillery preparation, matching pending exact-path work and
  atomic player/Bot region claims replace the duplicated parking ownership.
- Hydraulic Bots select physical five-point/full support from terrain attitude
  and missing contacts; every player vehicle stays on complete support. The
  integrated worker descriptor owns common weapon and mode observation.
- Stationary work survives sub-precision support jitter and recognizes checked
  current-point arc progress. The admitted pivot receives its first bounded
  refresh and matching native input; current executable points still win.
- First-trigger centre proof reaches the real plate beyond an interior sample.
  A sideways hydraulic endpoint cannot block its already proved chassis turn:
  the turn retains current correction before endpoint hydraulic aiming.
- Offset-fan arrival hands back to the authored route disk. Original route
  data, path search and driver laws have no diff from this follow-up's base
  `b9a360e14ef19416b332f9f3956cdbae51452628`.

Native results are specific to the scenes exercised:

| Runtime and report | Observed result |
| --- | --- |
| `42c0bcc0`, `071848-974d091b3a48`, S-51/203 mm, normal Mines 15v15 | Two standard HE and one explicitly selected premium HE player launches have terminal receipts. Friendly S-51 #14/#15 have terminal impacts and separate parking claims. This does not prove automatic premium selection. |
| `2a90535f`, `073812-f87a99d370fd`, all UDES 03, Mines | Nine player launches/terminals, 2,167 damage; two HE penetration shots, two consecutive HE fallback shots, then low-penetration APCR. This round exposed the subsequent sideways input defect. |
| `97cee192`, `075102-e56440f36026`, all UDES 03, Mittengard | Six player HE launches/terminals, 19 Bot terminal receipts, 1,234 damage; natural capture finish and no traceback. This map has no authored waiting places. |
| `97cee192`, round 2 of `075957-e56440f36026`, all UDES 03, Mines | 80 worker turn proofs, eight staged hydraulic inputs across five Bots, 75 Bot terminal receipts. #6 physically turned from yaw 1.890 to 0.643 and hit #26 at 07:55:02/19. #7 turned toward #19 and has an impact at 07:56:41. The player fired zero shots before death. |
| `8dab5e62`, `081315-63fbfad17585`, S-51/203 mm, normal Mines 15v15 | Two standard HE and two explicitly selected premium HE player launches have four terminal receipts. Friendly S-51 #14 has one terminal impact and #15 has two; those three ground impacts were not vehicle hits. Player region `p_19039905dbf1`, #14 `p_d6a5180aae4e` and #15 `spg_1_central_hills` are distinct. Natural team-elimination finish at 08:12:05; no traceback. |
| `8dab5e62`, `082611-c07e3dfbb219`, all UDES 03, Mines | Zero player shots before death, repeated stationary/hull review and combat releases; 89 worker turn proofs and 84 Bot terminal receipts. No final-trigger/world-refusal row was reached. Natural enemy capture finish at 08:23:40; no traceback. This is a failed player case. |
| `94169888`, `083145-5bd698e928cb`, all UDES 03, Mines | Four player HE penetration launches and four terminal receipts, plus 54 Bot terminal receipts at capture. The six new motion-pending samples show actual nonzero turn speed with zero vertical speed, not a measured vertical-jitter defect. No world-refusal row or traceback. This targeted test was stopped after player death, before natural battle completion; it is not full-round acceptance. |
| `94169888`, `084256-b26f907d56b3`, Object 261, normal Mines 15v15 | Stocks 9/9, five player launches/terminals: three standard HE and two premium HE, 477 damage. Settlements #2/#3 against #21 were both known non-direct zero-damage impacts; the policy requested premium HE at 08:39:31.935 and launched it at 08:40:06.679 (clock 403.292), before the explicit test stop/select command at clock 413.270/413.423. This proves the automatic switch; the later explicit selection is not credited as automatic. Friendly Bat.-Chatillon 155 #14 fired three terminal shots; friendly 261 #15 and enemy #29/#30 also have terminal receipts. Player and friendly #14/#15 regions are distinct. Natural capture finish at 08:42:32; no traceback. |
| `94169888`, round 2 of `085143-b26f907d56b3`, Bat.-Chatillon 155, normal Mines 15v15 | Stocks 18/18 and physical three-round clip. Standard HE #1/#2/#3 launched at 08:46:31/42 and 08:47:06, with three `2:p:1:*` terminal receipts and the full reload edge after #3. Different targets reset the miss streak; this round does not prove automatic premium selection. The explicit premium setup was cancelled by natural team elimination at 08:49:55 before readiness. No traceback. |
| `bf27cda9`, `090000-4c33dc60c74f`, Bat.-Chatillon 155, normal Mines 15v15 | Explicit premium setup completed with clip 3 and stocks 18/18. Three premium HE launches at 08:57:23/34/44 have terminal receipts. After #3 the policy automatically requested standard HE at 08:57:46.288; three subsequent standard HE launches at 08:58:59 and 08:59:10/32 also have terminal receipts. Six physical launches/terminals prove both clips and the return boundary. Checked dynamic logging observed a scattered ray blocked by friendly wreck #11 at 08:57:22.897, followed by an accepted launch less than a second later. No traceback. This targeted run stopped after both firing cycles, before natural battle completion. |
| `bf27cda9`, `091823-3e53ccc75856`, all UDES 03, Mines | Confirmed HE readiness (stock 13/13/14), one player HE launch/terminal at 09:11:57, 396 damage, then prolonged review/laying waits and player destruction. The final release was `native_pivot_stalled`; this is not acceptance of the remaining player problem. There were 82 Bot terminal receipts and no traceback. Natural enemy capture finish at 09:17:59. Mid-round capture `091527-3e53ccc75856` is also archived. |

The `97cee192` Mines player case remains unresolved: aligned/armour-passed candidates
were rejected as `auto_world_blocked`, but that runtime did not log the blocking
chord. The new checked-only `actual_world_refusal` includes the actual barrel,
aim point, centre/scatter blocker and chord. `bf27cda9` also covers the distinct
dynamic wreck/debris path, which can return the same refusal without crossing
the static-world logging branch. Dynamic lane refusals include their original
native witness and the checked centre/scattered polyline, not an invented
blocking chord. Friendly splash and missing lane geometry are included too.
Both added native-contact regressions fail before this diagnostic correction
and pass after it, including the unchecked no-record branch. No world collision or fire guard
was bypassed. The additional `8dab5e62` zero-shot case stalled before this
boundary; `94169888` now records actual speed, turn speed, vertical speed and
support flags only with detailed diagnostics enabled. The succeeding four-shot
case does not establish a root cause for either earlier failure. No settling
threshold was relaxed. Do not relabel either zero-shot round as acceptance. Complete native
waiting-place timing/turn acceptance also remains unproved by these reports.

The final all-UDES retest also leaves a reproducible pre-trigger stall after its
first shot. For target #16, sample 0 received `actual_enabled_hydraulic_input`
at 09:12:57 and 09:13:00/04; adjoining frames alternated with
`stationary_hull_review_pending` or `actual_hydraulic_point_pending`. At
09:13:11 sample 8 was reachable with failed penetration, while the finite HE
sweep still had no completed fallback comparison. The observed motion-pending
samples have real turn speed and zero vertical speed. These facts localize
this instance before final shot admission; they do not prove why the sweep/input
handoff fails to finish. Do not declare the UDES player stall fixed or remove
its support, armour or launch checks on this evidence.

Dense all-UDES latency remains a limitation. Mittengard server RTT median was
17.8 ms; worker frame median was 631 ms. Captured 30-second windows spent about
2.5–3.0 seconds in vertical support while actor work outside that stage and gun
aiming remained substantial. These captures do not isolate every contributor
and do not establish that all latency is fixed.

Final validation of `bf27cda9`: 69 player/shared control files, 1,376 cases, no
failures or skips; diagnostic-mode and trigger-refresh checks pass; CPython 2.7
source compile passes for 265 modules. Independent inspection verifies all 265
client bytecode modules, 268 paired server sources, 45 frozen launcher modules
and the native/recorder/editor package contracts. The precursor `94169888`
passed all eight jobs in [Tests run 1606](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/44429107170).
Exact final runtime CI: [Tests run 1607](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/44432063236)
passed all eight jobs: retained navigation, Bot behavior, native geometry,
client tests, Windows server/editor, Windows launcher/package and the native
exception trail.

Evidence retention: the production three-report limit pruned the earlier raw
`052258`, `050036` and `051141` ZIPs before they were archived. Their parsed
three-role logs and analyses remain, but the original ZIPs cannot be supplied.
All surviving and subsequent raw ZIPs are now archived separately under the
isolated QA `artillery-adaptive-20261119/report-archive` folder.

The dated notes below are audit history. Their intermediate pending statements
describe those revisions; the current result and limits above take precedence.

## November 19 — Sideways hydraulic handoff follow-up (native retest pending)

Report `wot-error-report-20261119-073812-f87a99d370fd.zip` ran `2a90535f`
through a full all-UDES Mines round. The player survived, committed nine real
launches with nine terminal receipts, completed 11 stationary-turn proofs and
dealt 2,167 damage. The first two HE launches were penetration, the next two
were fallback, and the following launch used low-penetration APCR. Workers
completed 117 turn proofs and 84 physical launches. This is positive firing and
return evidence, but not full acceptance: at 07:33:45 a proved turn toward #27
still received `hydraulic_pitch_limit` before native input and never started.
The actuator was checking an almost sideways ray against the current heading,
although its checked stationary endpoint was reachable after turning.

Shared hydraulic input now preserves the certificate's sequence: if current
pitch is unavailable but a fresh complete stationary turn and attackable
endpoint are proved, turn at the current correction first. The endpoint's
hydraulic correction is applied after current-heading geometry can consume it.
No unproved arc, blocked lane or stale observation gains motion or fire
permission. A real evaluator/native-input regression fails before the change;
removing its stationary proof still prevents native input. Pitch refusals and
this staged turn have additional inputs only with detailed diagnostics checked.
The normal native map picker also adopted the requested Mittengard map after
explicit window activation; the earlier ignored clicks do not establish a map
selection defect. This follow-up still needs native acceptance.

## November 19 — Physical SPG preparation and adaptive hydraulic Bots

Follow-up report `wot-error-report-20261119-052258-3a16d8e04a1a.zip`, runtime
`2eeac164`, exposed an unfinished native acceptance case: the last friendly
UDES 03 #7 and enemy #19 on the central Mines hill selected each other with
clear lanes but never completed their chassis-turn receipts. They repeatedly
entered and left siege mode. Basic support in travel mode still selected the
old independent coplanar-fit proof instead of the worker's physical five
contacts. This omission is corrected for worker actors in every mode. The
regression fails before the change on a supported 2 cm step and passes after
it; a missing intermediate contact still rejects the turn. Active-mode
projected angle refusals are not yet explained by that omission. Their exact
endpoint/body/hydraulic inputs are now recorded only when detailed diagnostics
is checked. This remains work in progress, not a completed native fix.

The follow-up native report `wot-error-report-20261119-055406-2ee42835f30a.zip`
ran `2b5fedc3` through a complete all-UDES round. Its endpoint diagnostics
separated travel-mode pitch refusals from the active-mode budget/reset loop;
the refusals captured during the round had no active hydraulic projection.
Source inspection and a failing worker regression exposed another binding
omission: common evaluation, trigger refresh, hydraulic leases and final
mechanical admission read the rendered Vehicle's descriptor, while worker
physics and weapons use the integrated actor's descriptor. A lagging mode or
republished display descriptor could therefore discard physical planning work
or inspect the travel gun after the native worker had enabled siege. Shared
source-descriptor reads now follow the actor observation binding. Players keep
their actual local native Vehicle; Bots use their integrated immutable mode
descriptor. A displayed-mode change cannot impersonate a physical switch or
retire an unchanged native gun. Checked-only mismatch records distinguish the
two sources. Native retesting of this correction is still required.

Native report `wot-error-report-20261119-060538-3454f01f2a70.zip` ran
`d5f26672` through a complete round. It captured real worker mode 2 with a
display descriptor whose hydraulic flag was still disabled. Weapon-identity
resets disappeared; 86 worker stationary-turn proofs completed. A remaining
review-liveness defect was also confirmed: current-target checked arc prefixes
advanced from 3 to 7 segments, yet the stopping lease expired because it counted
only completed point/armour reviews. The planner now reports the completed
support/collision/hydraulic prefix for this exact point call, independently of
its global support caches. Shared player/Bot stopping logic records a monotonic
per-point high-water mark for the current target and loaded shell. Only a fresh,
clear, still-progressing row with a larger checked prefix renews the existing
stall allowance. Other targets, stale/blocked rows, repeated prefixes, dependency
epoch changes and extra ground samples cannot renew it. No timeout or geometry
guard was relaxed. Native acceptance of this correction remains pending.

Report `wot-error-report-20261119-061811-637301543de0.zip` ran `3cd449ae`.
Checked worker arc progress was now observed, but a separate player/full-support
cache defect remained. At 06:13:42–44 the source stayed at approximately
(181.04204, 20.32813, 75.70489); support height changed about 0.0000002 m and
pitch about 0.000005 rad. Those variations fit the existing source precision,
yet exact repr-based support dependencies restarted the planner almost every
frame (epoch 271 to 315 in two seconds), preventing completed arc work. Support
stamps now contain numeric observations and retain the same anchor within the
existing 0.0001 m / 0.00001 rad precision. The comparison uses the original
anchor so cumulative drift still invalidates; support-owner changes and a
residual crossing the existing strict-plane boundary still invalidate too.
Neither contact queries, physical suspension, collision guards nor final fire
proof are changed. A regression fails before the fix and retains the certificate
for sub-precision measurement jitter afterward, while genuine height/normal
changes still retire it. Further invalidations include before/after support
observations only through the checked detailed-diagnostics entrance. Native
player/full-support retesting is still required.

Report `wot-error-report-20261119-063509-fb5d99538f67.zip` ran `46df4df7`.
Player full-support turn proofs now completed, but the player still fired no
round before death. A native refusal at 06:27:09 reached the selected interior
sample within micrometres, with passed armour and native alignment, yet reported
no target contact. The scan traces beyond that virtual sample to find real BSP
plates, while first-trigger centre proof stopped at the sample's aiming plane.
Real component bounding boxes can contain empty space before the plate. New AP
and HE regressions reproduce that discrepancy without replacing policy or
trigger verdicts. Centre proof now continues through the selected target's
observed native envelope in its relative-motion frame, using the physical
projectile chords and range cap. Every intervening world/vehicle collision,
native plate result, friendly lane and scattered launch proof remains required.
An intervening wall still refuses the trigger; moving inset plates can be proved;
an out-of-range plate cannot acquire permission. Native retesting is pending.

The `7597e37c` full-UDES round ended normally by team elimination at 06:54:01,
but the player still committed no shot. Review found an admitted-point conflict:
the active pivot retained sample 5 while global review supplied another sample
of the same target to the native actuator; the pivot then rejected the mismatch.
The real evaluator/actuator regression reproduces both the wrong sample and
the loss of its first bounded refresh after target motion. Shared evaluation
now prioritizes that admitted pivot's loaded-shell point before remaining work,
and hydraulic input uses its fresh row before another global sample. An already
executable point still fires immediately. Blocked points retain their demotion,
remaining work retains its budget, and no stale pose/line/armour/turn proof gains
permission. The existing mismatched-observation negative still rejects native
input. These regressions and all 69 player/shared control files pass; native
retesting of the point-priority correction is required.

Report `wot-error-report-20261119-071848-974d091b3a48.zip` ran `42c0bcc0`
with S-51, the observed 203 mm gun, player stocks 6/6, two friendly S-51s,
normal Mines and 15-versus-15. The map picker did not adopt the attempted
Malinovka selection, so this run must not be described as Malinovka acceptance.
Player standard HE launches at 07:14:25 and 07:15:07 both reached terminal
receipts; after explicit manual premium-HE setup, automatic launch at 07:16:21
reached its terminal receipt too. Friendly Bots #14 and #15 each have a terminal
impact at 07:16:51. Their regions `p_19039905dbf1` and `p_d6a5180aae4e`
differ from the player's `spg_1_central_hills`. The round ended naturally by
team elimination at 07:17:39. Neither exception file contains a traceback.
This proves the exercised preparation/parking paths, not every SPG/map or an
automatic premium-shell choice; the premium setup was manual.

Review of the new pivot priority added another failing boundary regression:
an already executable current sample must precede a pending admitted pivot.
The native input priority now yields to that current proof; its priority applies
only while the competing global sample is unproved. The prior pose-mismatch
negative and both admitted-point scheduling regressions remain intact. Native
all-UDES retesting is still required before delivery.

This is the latest authorized scope and supersedes the continuous hydraulic-Bot
policy in the historical section below. Every player vehicle stays on complete
support. Ordinary Bots retain their existing basic/edge switch. Hydraulic Bots
now use that switch plus terrain-attitude admission and a stable return. The
original route definitions, search, driver and final projectile collision rules
are preserved. PR119 remains unmerged; no tag or release is authorized.

Input report `wot-error-report-20261119-034847-62516ff5ea51.zip` ran runtime
`8a58cff9`. Its second round used S-51 on Malinovka, with two HE stocks of six.
There were two confirmed launch-preparation defects: a 1e-7 rad ideal-angle
gate rejected observed native barrel roundoff despite coarse alignment, and
pending current-target arc review withdrew fire permission and canceled the
already queued exact-path job. Preparation now uses the existing native 1e-5
rad precision and freezes dispersion around the actual barrel. The full exact
world-path receipt is still mandatory before ammunition or the shot sequence
can settle. An ideal level barrel retains the original deterministic scatter.
Matching pending target/shell metadata preserves a job; a real withdrawal,
changed source, target, loaded round or expired proof still retires it. Missing
preparation inputs now have separate reasons, with additional source snapshots
only through the checked detailed-diagnostics entrance.

The same report showed separate player/worker parking registries selecting the
same initial region. The server now atomically owns round-scoped region claims
for both actor types. Existing sourced position selection handles a refused
region. A pending claim holds translation without withdrawing legal firing
work. Transfer is atomic, a refused transfer keeps the previous claim, and
release, death, disconnection and the next round retire ownership. This changes
parking coordination, not the path search or movement mechanism.

The full-UDES input `wot-error-report-20261119-030736-f366e826de13.zip` showed
worker-frame latency rather than high network RTT. Complete support work was
a material contributor, including ground sampling and Python orchestration;
the native suspension kernel alone did not account for that cost. Hydraulic
Bots now select by terrain pitch/roll, excluding hydraulic aiming correction.
The explicitly custom selection policy uses 0.6 m footprint vertical excursion
for tilt admission (the existing basic upper reach), 0.3 m for return hysteresis,
and one continuous second of restored support. Any missing footprint witness
still admits complete support immediately. Neither native mode-transition edge
can downgrade it. A handoff preserves pose and velocities and never spends the
same physical time twice. Stationary hydraulic proof reads the current physical
owner: the same five supported witnesses for basic ownership, the detached
complete contact solve for full ownership. Five witnesses need support, not
coplanarity. Ownership also invalidates cached stationary certificates. This
does not grant rotation or fire before the retained collision and weapon checks.

The UDES report also demonstrated a fan endpoint outside the original six-metre
route-arrival disk. The original 13 m fan layout stays intact. Reaching its
local endpoint now latches a handoff to the authored goal through the original
navigator; the original route owner accepts its ordinary disk/crossing. The
vehicle does not have to reach the centre. The latch lasts only for that route
segment and does not change wait duration or safe-turn permissions.

Runtime candidate `9f520970` passed the 557 Bot-runtime cases and the targeted
player/shared controller suites (69 test files), plus the new physical-barrel,
pending-job, reservation and adaptive-support regressions. The independent
package inspection verified all 265 Python 2.7 client modules, 268 bundled
server sources, 45 frozen launcher modules and the unchanged native source
stamp. Native acceptance is in progress; results and final delivery identity
will be recorded here after report review.

The first packaged native run produced report
`wot-error-report-20261119-050036-cf9f6be4c3aa.zip` (S-51, normal Malinovka,
15 versus 15, player HE stocks 6/6). Player shots at 04:52:19, 04:53:03 and
04:54:07 each have a server terminal receipt. Friendly S-51 #29 also has
terminal receipts at 04:53:15 and 04:54:09. The shared reservation rejected
#29's duplicate east-region proposal and reassigned it to the central field;
the player and the other friendly SPG retained distinct regions. The complete
battle ended by team elimination at 04:58:19, rather than a test-process kill.
Neither exception record contains an exception beyond its session header.

Review also found a second 1e-7 prerequisite in the player's native source
inversion. A regression quantizing the inverse to a 4e-6 grid (inside the
existing 1e-5 native contract) reproduced 120 ticks with no launch. The source
inversion now uses the same native precision as preparation; the regression
then launches and settles exactly one physical round. This is not a relaxation
of the exact world path, friendly lane, target-motion or final launch checks.
The updated native package is being retested before delivery.

## November 19 — Complete support and stationary combat handoff

This section supersedes the hydraulic-support exception in the earlier audit.
The user now explicitly requires continuous complete support for every player
vehicle and every hydraulic Bot, in travel, transition and siege modes. Other
Bots retain the existing basic/detailed support switch. Preserve the original
route/search mechanism. A route wait prohibits forward/reverse driving but
allows a physically checked turn; its arrival and duration clocks stay owned
by the original parking task.

Reports `wot-error-report-20261119-012026-8a0039accc31.zip` and the later full
snapshot `wot-error-report-20261119-012203-8a0039accc31.zip` run runtime
`29c33dea`. In the second round, Strv 103-0 #8 was destroyed at 01:17:14.
Pending/obstructed inspections of other vehicles renewed the player's stop
until 01:17:53. At the later capture position, repeated siege entries and
releases produced no player launch after 01:19:56. Jagdtiger #10 destroyed
the player at 01:21:33. Mode acknowledgements themselves completed normally.
A local reproduction separately demonstrated lost mode-entry point identity:
a circle entry with no policy candidate saved no point, release saved no
failed point, and the unchanged line could immediately reacquire the mode.

The previous Bot support hook was still incompatible: the movement owner
accepted all five footprint witnesses, but stationary aiming compared a new
five-column fitted attitude with the Bot's accepted dynamic attitude at
1e-5 rad. The player hydraulic class was also explicitly excluded from the
complete contact solver whenever the active native hydraulic flag matched.
That did not provide the required continuous complete support guarantee.

The correction enables the existing complete contact model for hydraulic
chassis and keeps their hydraulic actuator separate from the chassis frame.
The exact #1513 `physics_shared.initVehiclePhysicsClient` bytecode confirms
zero hydraulic hard ratio and separate native mode spring-length caches.
The existing stiffness/damping/inertia reconstruction remains a reconstruction;
this change does not claim to retrieve the native solver's hidden constants.
A detached zero-time complete-contact solve replaces the independent five-ray
attitude comparison. It cannot commit movement or fire. Complete collision
arcs, source checks and actual first-trigger proof remain required.

Parking retains translation ownership. An admitted stationary turn can use
the common hull/siege input, with the original wait-area bounds and native
collision/support checks. Another candidate, an obstruction or pending query
cannot restart the stopping clock. A departed target only hands over to a
currently clear proposal; otherwise navigation resumes. Siege entry retains
the actual point, uses two-second clear-line confirmation, waits for the
native enabled acknowledgement, and only then evaluates gun angles. Release
fences the failed current-shell points without borrowing another shell's
failure. Native acceptance and final package/CI identity are recorded below
only after they have actually completed.

The first normal-battle follow-up exposed an additional class-identity error.
Report `wot-error-report-20261119-023524-c2c18cb01c0d.zip` contains 29 UDES 03
Bots, but only 23 complete-dynamics records and 175 legacy five-column fitted
support refusals. Native active child descriptors do not consistently retain
the outer hydraulic capability flag. Runtime `bd01e331` therefore retains
complete support from the installed travel/siege descriptor pair in all four
mode states. A regression now uses a travel child with its hydraulic flag
absent/false and a separate enabled child; it no longer models every mode by
changing only an integer on one permanently flagged descriptor. Ordinary Bot
support switching remains unchanged. Expanded continuous-contact diagnostics
are emitted only with detailed diagnostics checked.

The next native run caught a second production admission omission before
acceptance: the worker installs the existing bounded column reader in its
`wreck_ground_probe` seam, while unit fixtures installed a dedicated trial
reader. The live-Bot guard still restricted that seam to edge recovery, so
selecting continuous support did not actually start the complete solve.
Runtime `15d7ed96` admits the same existing reader for continuous hydraulic
support as well. The cross-mode regression now uses the production callback
wiring, not the dedicated test callback. No new ray rule or navigation input
is introduced.

The completed `15d7ed96` normal-battle follow-up finally records continuous
complete dynamics for all 29 UDES Bots. It also isolates a transient proof
handoff: `_install_bot_descriptor` correctly clears mode-specific spring
parameters, but `complete_support()` used cache presence as solver ownership.
During that gap, a plan incorrectly selected the five-column sampler. The
follow-up `8a58cff9` follows the continuous owner through parameter rebuilding.
Its regression clears the cache in each of the four native mode states.

The same native round contained no player launch: actual centre-ray armor
refusals and misses rejected the prepared HE point before a trigger was
submitted. This is not claimed as a successful player HE firing test or as a
confirmed cause in the new support solver. Only opt-in `actual_barrel_refusal`
evidence is added: selected point, observed barrel origin/direction, centre
endpoint, source pose and the already-computed first material contact. The
existing predicates, penetration factor, thresholds and debit/launch boundary
are unchanged; logging neither requests another geometry query nor grants fire.

### Frozen runtime validation and package

Runtime `8a58cff96ec773dc463aff2b1cc4909fc711afc5` passed 31 final related
test files (all shared-control files, the complete first-trigger admission
file and hydraulic stationary planning). Cross-mode native-reader activation
and the diagnostic checkbox regressions passed separately. Earlier broad
coverage exercised 533 client files; the one initial failure was a fixture
that changed Bot identity to human only after admission. Its corrected setup
and complete navigation-command assertions pass. Windows-host reference
checks explicitly use the existing engine-free fallback; they are not native
physics acceptance.

The former hydraulic-exclusion and plane-only fixtures now assert complete
contact ownership and real source/arc observations. Existing production
position/angle thresholds remain 0.1 mm and 1e-5 rad. The full-contact endpoint
fixture uses that unchanged position contract for its independently solved
micrometre-scale height difference, rather than seven-decimal plane identity.
Navigation-command comparisons, blocked-shot refusal and no-debit assertions
remain required.

The user permitted an additional normal battle with waiting points, such as
Mittengard. The canonical `100_thepit` routes currently contain no wait
extensions. The normal Mines (`10_hills`) TD routes have three independent
60-second waiting places per side, so those unchanged routes were used with
30 elite UDES 03 slots, one occupied by the player. No default route, search,
driver or navigation graph was edited in this follow-up.

Final-runtime report `wot-error-report-20261119-030736-f366e826de13.zip`
captures the normal-battle stress test before changing fixtures, not a
completed match. All 29 Bots have complete physical dynamics (1,023 records).
The existing model uses ten springs and twelve ordinary auxiliary contacts,
adding its existing rigid-body contacts when tipping. Both client roles have
zero legacy fitted-plane refusals in this report. Seven Bots entered authored
parking tasks; their diagnostic spans reach 59.97 seconds. Translation was
never admitted in those parking records, and Bot #11 has fourteen admitted
turn observations. The player's stock was 13/13/14; explicit test setup loaded
HE compact 3722 and received `shell_ready` before restoring automation. Server
launches `1:p:1:1` at 03:05:58 and `1:p:1:2` at 03:06:06 both use shell index 2
and have matching impact terminals. Ten Bot launch terminals are also present.
This does not claim every vehicle, slope or first-trigger refusal is fixed.
The all-UDES diagnostic stress scene still showed substantial callback delay
and traffic congestion; those observations are retained, not bypassed by
relaxing support/fire predicates or changing original navigation.

The final original mixed 15-versus-15 Redshire scene is captured in
`wot-error-report-20261119-031731-633e4de7605a.zip`. Explicit test setup again
received `shell_ready` for HE before restoring automation. The player launched
one HE round at 03:13:23 (`1:p:1:1`, shell index 2), with a matching impact
terminal after 60 ms. The player survived; the match ended at 03:14:32 by the
opposing team's base capture. The server recorded 167 Bot projectile terminals.
All three UDES Bots have complete dynamics; two ordinary ELC Bots temporarily
used the existing detailed edge path. The 70 legacy fitted-plane refusals
belong to ordinary Bots, not the player or UDES actors. They are retained as
observations, not silently reclassified as successful support. The player has
20 full-contact support observations and no legacy fitted-plane refusal.
Two clear-line entry episodes each confirm for approximately two seconds,
then retain engagement through native state 1 until state 2 is acknowledged.
Obstructed-point review remains visible between these episodes; this evidence
does not establish that every long aiming delay has been eliminated. The new
opt-in barrel record was exercised by an ordinary Bot's actual armor refusal,
including its own source pose and first contact. No fire rule was relaxed.

The exact packaged runtime passed all eight jobs in
[Tests run 44375799851](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/44375799851),
including the complete client/launcher suites, Bot behavior, retained-route
checks, native geometry, Windows launcher/server and native exception trail.
The handoff update after that runtime is documentation only. Both native
reports remain in the isolated QA reports folder; their reassembled per-role
audits are retained in the local `qa-pr119-parity-20261118/support-wait-20261119`
evidence directory. The isolated test clients and launcher were closed after
report review.

The Windows test ZIP is `wot_PR119_8a58cff9_Windows_2026-11-19.zip`
(68,291,555 bytes; 1,298 members), build `local-pr119-8a58cff9`. Independent
inspection verified all 264 Python 2.7 client modules, 267 paired server
sources, 45 frozen launcher modules, native-math/source identity, recorder,
editor and native starter; ZIP CRC/inventory checks passed. The intermediate
`bd01e331` and `15d7ed96` ZIPs were moved out of Downloads as superseded QA
artifacts. The original PR119 remains open and unmerged.


## November 19 — Complete player-mechanism migration audit

The user clarified the scope: migrate the complete existing player mechanisms
to Bots, including their handoffs. Do not narrow migration to target selection
or combat entry. When correcting bugs, preserve the original pathfinding
mechanism as far as possible and correct combat/ownership handoffs instead.

One intentional physical difference must remain: the user identifies the
Bot five-point/full-support switch as the 1.1 bridge-edge fix and performance
optimization. Ordinary Bots normally use basic support, temporarily admit
detailed support on loss of a footprint witness, and return after support is
restored. Ordinary players continuously use detailed support. This difference
is not an incomplete migration. Hydraulic chassis retain their existing
special support path on both actors. Neither the support-mode selection nor
the existing route/search/driver implementation is changed by this follow-up.

The earlier claim that migration was complete was unsupported. Sharing a
policy constructor and passing selected regressions did not establish that
every physical interface or continuation reached that policy. The audit now
traces the full player control surface into each Bot consumer:

| Mechanism | Player and Bot owner / boundary | Evidence and remaining acceptance |
| --- | --- | --- |
| Actor identity, native source, mounted weapon and mode | `PlayerObservation` / `BotControlBinding` | Full public observation contract checked, including every property and method; source independence tests forbid reading the observer's tank. |
| Visibility, radio rights and public roster | `SharedOrderPlanning`, common geometry and actor-scoped native observations | Shared order/spotting/roster regressions; same-round identity does not grant hidden spatial observations. |
| Strategic tasks, priority, explicit orders, arrival, hold and retry | `BotPlanner`, `MissionControl`, `HaltObservation` | Both actor classes inherit every common task method without replacement; mission and order tests compare both actors. |
| Original route, local movement, traffic and recovery inputs | Common `BotRuntime` / driver; native actor adapters | Original search/driver sources unchanged. Navigation and movement receipt comparisons retained. |
| Combat acquisition, continuity, two-second entry, no-HE cooldown | `CombatStop`, `CombatControl` | Common ownership and actor-entry tests, including immediate same-engagement handoff and five-second no-HE exit. |
| Point and vehicle order, blocked-point skip/reopen, bounded moving-source work | `AttackPolicy`, `NativeAttackEvaluator`, `OrderedAttack` | Finite frontier and target-handoff tests. Native all-blocked and newly clear outcomes remain independently checked. |
| Penetration/damage ordering, primary premium HE, current-car HE and blast ranking | Common ammunition validation and ordered policy | Gun/shell whitelist, actual inventory identities and full current-car point tests; primary HESH is not ordinary fallback. |
| NEXT/CURRENT inputs, magazines, trigger groups, actual-shot return counters | `CombatControl` over native gun/ammo observations | Readiness, exact stock, queued-vs-loaded and committed-shot/clip tests; no simulated debit. |
| Aim continuity, actual barrel readiness and capture gun handoff | `SharedEngineControl`, native aim adapters, common combat owner | Moving native feedback and exact unchanged parking-control regressions; replacement native Bot #20 consumed the new post-movement circle handoff. The player died before circle entry. |
| Siege transition, hydraulic pose and stationary turn certificates | Common siege helpers and `StationaryPlanner` over actor observations | Missing Bot support input and direct rendered-mode reads found and corrected; uneven five-column Bot projection regression fails before the correction and passes after. |
| First-edge proof, frozen dispersion/penetration draw and trigger tail | `TriggerAdmission`, common preparation; native physical weapon owns commits | Shared material/obstruction/scatter/pose tests and worker commit/publish tests. A Bot-specific scatter-reopen omission was found and corrected. |
| Projectile send/retry, hit and terminal receipt, artillery shell cycle | Native actor transports, common projectile protocol and `ShotPolicy` | Frozen publication/retry and artillery receipt tests; server terminal records are required in native acceptance. |
| Repair, crew/device effects, consumables, governor and passive equipment | Common `EquipmentState`, `_poll_bot_equipments`, critical/fitting laws | Player facade observes native equipment and submits native inputs; Bot uses its own canonical ledger through the same policy. Equipment and critical-mechanic regression files are included in the full run. |
| Death, reload, replacement actor/gun, release and lifecycle | Common mission/combat owners with native actor bindings | Ownership/lifecycle/tail tests; a retired controller does not cancel an already committed native trigger tail. |
| Diagnostic entrance and unavailable/null physical observations | Detailed-diagnostics guard and actor-scoped records | New missing-shot and scatter-recheck exception records are opt-in; disabled logging is tested to collect neither payload. |

The `291b51b6` native Conway round was not complete migration acceptance.
Report `000117-3c894d2c2ed1` includes every expected launcher/server/client role.
The mounted gun was BL 5.5 inch, with actual 10/10/10 ammunition and explicitly
loaded HESH before automation. Five actual HESH commits reduced stock to five;
the fifth shot at 00:00:10 selected Object 261 #14, with a matching server
launch and impact. The target died before the player reached the circle.
This demonstrates the earlier ignored-261 path firing, not a circle test.

The user also correctly observed that enemy UDES #9 and #10 did not fire.
Neither has a server projectile terminal. #9 retained clear human-target
points but repeatedly stalled on stationary projection and released twice
with `siege_stationary_review_stalled`. Its old generic five-point plane fit
rejected a 0.052828 m residual. The Bot binding omitted `chassis_support_at`,
so the shared hydraulic certificate could not call the existing chassis
support solver. The new binding reads the same five native chassis columns;
it does not change the daily basic/detailed support switch or the solver.

The complete shared-mode audit also found direct reads of the rendered
`Vehicle.siegeState` in combat ownership, mode-entry/review, hydraulic pose
and hydraulic-input leases. A worker's integrated mode may already be enabled
while that presentation still shows transition. These consumers now use the
actor's existing native-mode observation. Disabled and transitioning modes
still defer aiming; paired descriptor, pose and pending-input checks remain.

An additional continuation omission made scatter-obstructed Bot points
permanent: the policy looked only on a player's controller for its admission
owner, and the recheck read the foreground player's effective shell. Bots now
use their own existing admission owner and an explicit actor source-shot
observation. First-edge preparation and read-only rechecks use that same Bot
projection. The new regression proves refusal with a world obstruction,
restoration after removing it, retention of the same native draw, no debit,
and no foreground-shell read. Final proof predicates and thresholds are
unchanged. Missing native-shot/recheck inputs receive detailed records only
when the diagnostic option is selected.

All common combat and mission methods are now covered by the no-shadow-owner
contract, rather than a five-method sample. The complete client reference
suite passed 533 isolated files / 10,829 cases. Four affected files were
rerun after the final interface/diagnostic assertions and passed. CPython
2.7.18 compiled all 264 client modules. These are engine-free reference
checks, not native acceptance.

### Replacement native results and package

Runtime `29c33dea21a7bbbb1863941297a95d1c0e0123cc` was packaged and extracted
again before starting the actual Chinese HD #1513 client. The original
Redshire 15 vs 15 lineup was retained, with the player's large-TD slot using
Conway BL 5.5 inch. A completed test-channel receipt confirms actual HESH
32602, one ready round and AP/HESH/HE 10/10/10 before automatic inputs resume.
This setup remains an explicit test input, not an automatic policy switch.

Final report `wot-error-report-20261119-004053-6dfc12f3418f.zip` contains every
expected launcher/server/visible-client/hidden-worker role. Both client logs
contain no traceback, hydraulic body disagreement or missing-input diagnostic.
All four UDES Bots have actual server projectile impact receipts: #9 has six,
#10 two, #24 six and #25 ten. Enemy #9 and #10 selected the human and actually
hit Conway; this replaces the former zero-shot observation. The player was
destroyed during the fight. This is not evidence that the player reached or
fired from the capture circle.

Native Bot #20 reproduced the circle movement/gun boundary: the pre-movement
handoff refused its original parking turn, and four post-movement callbacks
accepted the same fresh reachable point on Bat.-Chatillon 155 #15. The original
turn/throttle remained in force. There is no subsequent #20 projectile commit
in that brief target window, so this proves native handoff consumption only.
The complete player capture regression independently proves a real commit
after the recorded small parking correction and forbids a stale cached fire
edge. Native player circle firing remains a coverage boundary for user testing.

The observed road shell changes were also audited and accepted by the user.
At 00:28:13, HESH had four obstructed and five armour-failed points on the only
then-admitted target, O-Ho #13. AP was requested during route observation.
Actual AP shots committed at 00:28:24 and 00:28:35. The second edge queued
HESH as the return shell; actual HESH fired at 00:28:54. Final stock is AP 8 /
HESH 9 / basic HE 10. No basic HE fallback shot was fired in this round.

The discussion did not authorize a new ammunition rule. Whitelisted HESH
remains a penetration primary followed by AP, then available HE fallback.
Ordinary HE tests only its current vehicle, skips obstruction and ranks blast
damage if it cannot penetrate. Consecutive fallback commits control return;
valid whole-round low-penetration failure can defer it. The existing zero-
expected-damage fallback boundary is recorded, not silently changed.

Exact-runtime [CI run 44346628708](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/44346628708)
passed every job: behavior, navigation, native geometry, Windows server/editor,
complete client/launcher tests, native exception trail and Windows launcher.

Windows candidate: `C:/Users/USER/Downloads/wot_PR119_29c33dea_Windows_2026-11-19.zip`.
Size: 68,189,940 bytes; 1,298 members.
SHA-256: `e400292a13b9ddeb27615778adf10cb9a8af3ca6b629fb55f2815e75a306ea0e`.
Build identity: `local-pr119-29c33dea-actor-observations`.
The native round used this ZIP's fresh extraction, not a different development
directory. Independent package verification matches 45 frozen launcher modules,
267 paired server sources and all 264 Python 2.7 client modules; 306 wotmod
members validate. Native math/starter match current sources, the embedded
recorder executes, and the packaged editor smoke test passes. Existing CI
native/UI/recorder assets were preserved. `ai/` search/driver sources and
`vehicle_physics.py` are unchanged relative to the reviewed starting head.
PR #119 remains open and unmerged.

## November 18 follow-up — Actor parity, finite blocked review and hydraulic pose

The `201622-fb0bb6f40e74` report establishes two separate ELC defects.
Bot #7 saw Object 261 #29 before reaching the capture circle, but automatic
capture travel admitted ordinary players only. Inside the circle, clear,
penetrable HE points still lost gun handoff because the saved parking anchor
was 7.995 m from the actual vehicle. The vehicle was already inside the
50 m capture area. The same anchor mismatch affected ELC #21.

Production Bot and player-siege constructors also selected the old penetration
policy while ordinary players selected ordered review. Same-fact regressions
on original commit `7b08b4be` fail for both omitted entries: remaining points
on the current vehicle, APCR before HE, and two committed high-penetration
single shots before returning to the lowest penetration shell.

All ordinary actors now select the existing ordered policy. Artillery retains
its explicit artillery branches. The common policy owns penetration/damage
ordering, current-car point review, target sweep, next load, committed-shot
return, and no-HE exit. Route admission uses two seconds for every actor;
the existing five-second no-HE cooldown and native siege mode echo still
apply. Automatic capture approach and circle hold no longer exclude Bots or
player siege vehicles. Gun handoff in a stopped capture area uses actual
circle membership, movement intent and unchanged chassis inputs, rather than
requiring arrival within 1.5 m of an obsolete anchor.

Fully blocked HE contacts move to the end of a finite review queue. Other
vehicles receive foreground inspection even without spare atomic capacity.
After all alternatives fail, the original contact receives one fresh final
revisit before existing checked position recovery or route release. Moving
the source preserves completed inspection work, not old firing evidence.
Contact/sample/load/round changes and failed observation fences retire the
relevant work. Fresh clear observations restore points immediately. A clear
alternative continues the same engagement without a new route timer. HE
penetration and maximum expected blast damage remain within the current car.

The report also contains 22 hydraulic projection errors. In one complete
Bot #24 observation at 20:12:09.195, Euler pitch addition retained chassis
yaw while local hydraulic composition changed body yaw by 2.576663 degrees.
The worker aim/review, gun source and native presentation now use one local
pivot composition. Chassis integration retains its existing state layout;
the derived body pose does not overwrite driver yaw or ground support.
The worker publishes the hydraulic correction through the existing compact
state row; client presentation uses that correction once, instead of a second
independent native hydraulic predictor. Rendered hull and ground collision
matrices retain their separate owners. The paired server and client must
ship together. Existing support, collision and final trigger checks remain.

New detailed evidence covers Bot hydraulic inputs and circle gun handoff;
both builders are guarded by the detailed diagnostics entrance. No new
diagnostic payload is collected with that option disabled.

Local validation includes constructor parity, actual commit counters, finite
moving-source review with atomic work disabled, same-engagement front-enemy
handoff, circle-anchor offset, local-pivot matrices and wire roundtrip.
Legacy recovery fixtures explicitly establish an engagement where they test
continuity; cold blocked route cases retain full route/control comparisons.
Reentry cases now require current clear evidence throughout two seconds.
The legacy wire-column digest is preserved after removing the new appended
hydraulic column; it was not replaced with a new expected digest.
The expanded scoped run passed 2539 cases in 82 isolated files. This is the
engine-free reference branch used by Linux CI, selected explicitly in an
external Windows-host harness; it is not native Windows acceptance. Each
test retains its original production policy, geometry consumers and assertions.
CPython 2.7.18 also compiled all 264 client modules.

The first native Redshire 15 vs 15 round used runtime `d8293ff6`, paired CI
launcher build `colorfulmeans-44319287219-1`, on Chinese HD #1513. Completed
test-channel receipts establish player UDES 03's actual HE 3722 load with
13 AP / 13 APCR / 14 HE before automatic control resumed. Clear route evidence
qualified for 2.016 seconds before siege was requested. Four accepted native
triggers fired HE, reducing its stock from 14 to 10. The exported session
`222416-1644d8118b66` includes all launcher, server, player and worker roles;
none is missing. Neither client role contains a traceback or hydraulic pose
disagreement. This intermediate round exposed the premium-HE primary-role
gap below; it does not validate the later correction.

### Premium HE primary roles and reopened points

The gun/shell whitelist is a primary penetration role, not only permission to
inspect more HE points. The five exact #1513 pairs now enter the common
penetration sequence. In particular, Conway 5.5-inch HESH precedes its AP
backup. The manually proportioned test rack retains every stocked shell,
including basic HE; applying primary roles no longer starts these Bots on AP.
Ordinary HE still reviews only its current vehicle. Primary HESH sweeps targets
and then its penetration backup before HE fallback. Physical HE kind, damage
and actual launch checks are unchanged. Two committed fallback shots, or the
existing magazine boundary, control return; penetrating primary HE is not
counted as fallback. Explicit manual selection starts that shell's primary role.

Additional consumer regressions identified stale inspection work hiding a
fresh clear point, and an all-unusable HE damage comparison that never reopened
after its obstruction disappeared. Fresh observations now retire those obsolete
work records. HE retains a completed comparison through small source movement,
then reproves its winning point before aiming; a changed observation fence
revokes all firing rows. Known physical recovery is allowed to finish its
existing bounded native probe instead of being cancelled by completed work
history. The original driver, support proof and trigger admission are unchanged.

The next native player is Conway `uk:GB81_FV4004` with `_5_5inch_AT_Gun`,
capacity 30 and a 10/10/10 AP/HESH/HE rack. Its 120 mm alternative is rejected
by the test entrance. It replaces the human's large-TD slot only; the other
29 Bots retain the original lineup. The following intermediate rounds and
November 19 section record native follow-up and the replacement package.
PR #119 remains open and unmerged.

### Native Conway round and remaining hydraulic consumers

The native garage explicitly showed BL 5.5 inch installed and 120 mm AT L1A1
uninstalled. The `046f959c` round acknowledged HESH compact descriptor 32602,
slot 1, one ready round and the complete 10/10/10 rack before control resumed.
The setup selection was an explicit test-channel input, not an automatic
policy switch. Server launch and terminal records match all three commits:
HESH at 23:11:03 (miss), HESH at 23:11:14 (impact), and basic HE fallback at
23:11:37 (miss). AP was loaded and reviewed between the second and third
shots, but no AP cartridge was fired. The postbattle result recorded 915
damage and one kill. All four UDES Bots have actual projectile terminal records.
Bot 183 initialized on HESH slot 1 while retaining the complete equal-ratio
inventory. Report `232357-1c3e3418bf1f` contains every expected role.

Exact-head CI for `046f959c` passed behavior, navigation, native geometry,
Windows server and Windows editor jobs, plus all 49 launcher test files.
The full client run passed 531/533 files. The remaining two files identified
one real hydraulic omission and outdated load-receipt expectations.

The side-slope physical-launch test still used the uncomposed chassis angles
in the existing hull-laying input. It now receives the same composed gun-body
pose as barrel laying. The circle gun-handoff comparison uses that pose too,
so its preserved-control check agrees with the input it compares. A separate
native callback assertion also caught a 0.528 m launch-source discrepancy in
the same fixture: the final launch builder still copied the old Euler pose.
Exact-origin review and launch now share one canonical source-state builder.
No movement law, support certificate or trigger predicate was relaxed.

The binding regressions now distinguish the consumed cartridge from committed
NEXT during a full reload, and assert actual promotion only at native readiness.
They retain exact stock counts, elapsed-clock checks and explicit CURRENT-input
coverage. Unreviewed HE cannot displace the already stocked fallback using a
bare policy reason. The native follow-up below uses the resulting payload.

### Native green-point and capture-gun regressions

All CI jobs passed at runtime `914c9bc3`, including 533 client test files and
49 launcher files. The native Conway round still exposed two real faults,
reported by the user while watching. Report `233445-069a04553412` preserves
both; green CI is not acceptance of these native behaviors.

Before entering the circle, Type 4 Heavy #12 had clear, passed native points
with AP ready. At 23:32:42-46, the extra gun-aligned predicate continued to
reject normal asynchronous tracking lag. At 23:32:47 it became
`native_lay_stalled` and released the route. The input-inversion precision
constant (0.00001 radians) had also been used as a tracking completion test.
It is now retained for its actual inverse/ABI purpose. Ordinary foreground
tracking observes the current real barrel at the selected point using the
existing first-edge 0.30 m point window. The original first-edge owner still
repeats mechanical, actual-path, material, scatter, obstruction and freshness
proofs; none of its predicates or constants was changed. A complete moving
target regression reproduced the former permanent unaligned state with a
one-frame native rotator echo, then reached a real committed shot after the fix.

Inside the circle, Object 261 #14 was selected from 23:33:13 onward. Gun
handoff repeatedly failed while the native input stayed on hull-forward rest.
The original parking correction was small but nonzero (for example
-0.0006790279131036106). Donating a limited-turret target before the chassis
law would zero that original correction, so the early guard correctly refused
the movement change. The missing operation was a gun-only handoff after the
original movement had already executed. That existing weapon boundary now
consumes the same current reachable candidate for aiming and first-edge fire,
without changing any movement field or rerunning the driver. The regression
uses the recorded correction and compares all navigation/control fields.
Hull-laying points still require the original support/rotation owner.

Detailed diagnostics add current-barrel point error and the handoff boundary;
the payload builders run only when detailed combat logging is selected.
The final replacement package and native verification are recorded below.

## November 12 follow-up — Finish obstructed HE engagements

The `214138-c65b14d3ce9e` report showed UDES 03 holding Type 4 Heavy #12
through repeated blocked-point and firing-position decisions. The siege
consumer parked the vehicle before calling position recovery. Progress in
the shared chassis caches extended the stop even when the retained point
had no useful new result.

The loaded HE review uses the same current-target sweep on ordinary,
siege and worker vehicles. A checked obstruction removes the point from
the sweep. A fresh clear result restores it. The loaded shell ranks
penetration and HE contact within that target. An exhausted blocked
target can hand off to a candidate with a checked clear lane in the
same engagement. The candidate's own HE sweep begins after the handoff.
Spare foreground work may check an alternative lane within the current
callback. A pending alternative does not extend the stop.

A stable blockage can enter the existing same-point position probe when
combat owns movement. The probe checks a candidate route segment and the
future lane. Unsuccessful position review returns the original task.
The stationary hold clock uses newly completed point receipts for the
held target and shell. Native siege mode still controls when aim may be
evaluated. The existing five-point support, driver and actual launch
checks authorize their respective operations. Combat handoff details
use the existing detailed diagnostic logging switch.

The first two Windows rounds on `523fc56f` exercised the position probe
and exposed a stale target after native mode reentry. At 22:41:51.277
the confirmed approach chose #10, while the HE sweep resumed #13.
`b37bd79c` carries the confirmed contact across the enabled-mode echo.
The regression keeps the old target visible while proving that the new
engagement reviews only the confirmed target.

Windows HD #1513 ran the final build in the same Redshire 15 vs 15
mobile-combat scenario with player UDES 03 on team 2. The launcher test
channel confirmed shell descriptor 3722 in slot 2 at 22:47:31, with
one chambered round, zero reload and a 13/13/14 rack. Automatic drive
and fire then resumed.

- At 22:49:44.454 the player fired HE at #5. The server recorded the
  matching impact. Engagement 4 transferred from #5 to #12 at
  22:49:44.604 without a new route confirmation.
- At 22:49:44.822 all nine HE penetration samples on #12 were
  `world_blocked`. The current shell remained HE while reloading.
  The existing recovery probe returned `point_recovery_no_checked_position`
  at 22:49:45.170. The route regained control. After travel mode resumed,
  the player moved 103.27 m by 22:50:26.032.
- At 22:50:30.129 a newly clear point on #12 qualified after 2.019 s.
  At 22:50:33.216 the enabled siege observation again confirmed all nine
  points blocked, with HE chambered and zero reload. The position review
  exhausted its existing six-second budget and released at 22:50:39.241.
  A later approach obtained 2.016 s of clear evidence and entered siege
  again. Several points cleared while support was still unsettled.
  No player round was launched at #12 in this session. The full-block
  handoff to an already clear alternative was covered by a focused
  regression. The observed live full-block cases exercised position
  review and route release.

Runtime `b37bd79c96b543123822144d3e3f9996ad7c082c` passed 283 cases in
14 isolated unittest files covering HE, ownership, siege and launch
admission, support, capture, and the mobile-combat scenario. The extra
host-worker tests requiring the native simulation and two burst
diagnostic assertions reproduce their failures on `fa243753`.
CPython 2.7 compiled all 264 client modules. The Windows ZIP contains the
rebuilt client and current staged server files with the existing x64
launcher executable. The x86 native source stamp, archive CRCs and
installed client payload were verified. The package is
`wot_PR119_b37bd79c_Windows_2026-11-12.zip`.

The final report is `wot-error-report-20261112-225128-a940d3514e72.zip`.
It passed CRC verification and contains the launcher, server, visible
client and hidden worker logs. The launcher deliberately ended the
session after collecting the obstruction and route evidence.

The earlier two-round report
`wot-error-report-20261112-224433-e587ff68a7aa.zip` records the HUD
latency and enemy UDES observation. Around 22:37 the visible HUD ping
was the hidden worker's frame interval. Logged worker samples were
172–307 ms and the local server round trip was 7–14 ms in that interval.
Worker profiling attributed the largest recorded cost to Bot simulation
slices. Enemy UDES 03 #9 repeatedly released a stationary review and
reentered siege. The mode changes reset and then recomputed the hydraulic
pitch target. Continuous barrel motion within enabled siege still needs
matching requested and actual pitch samples.

## November 12 follow-up — Five-point hydraulic chassis support

In report `wot-error-report-20261112-195726-acf29a5596d3.zip`, the player
changed from #13 to #4 in the same engagement. The stationary review rejected
the starting pose repeatedly. The five armour-box ground samples produced a
fit residual of 0.097292 m against the review tolerance of 0.0001 m.
The earlier real turn at the same X/Z had valid track support and changed
support height by 0.019266 m over about 36 degrees.

The player hydraulic review now uses the five chassis columns and the
supporting-face calculation shared with the existing local vertical motion.
The sampled heights, pitch and roll feed the planned turn and its collision
checks. Each slice has an independently checked middle and end. The last
checked support pose must agree with the pose used for the projected aim.
The existing combat controller consumes a completed motion proof. The
actual-barrel and first-trigger validation remain the fire authority.
The driving caller retains its original support, straddle and fall decisions.
The worker uses its own physical observations.

The **Collect detailed diagnostic logs** checkbox enables
`stationary_chassis_support` records. Each emitted record includes all five
columns, hit coordinates, surface normals and layer decisions from the
existing queries. The report had 49 such player records with valid support,
including a 0.103948 m gap from one sampled point to the supporting face.

Windows HD #1513 ran two rounds of the same Redshire mobile-combat 15 vs 15
scenario with player UDES 03 on team 2. The launcher test control confirmed
HE descriptor 3722, slot 2, one chambered round and zero reload before
automatic control resumed in each round. Both ammo racks were 13/13/14.

- Round 1. At 21:12:02.748 a 14-slice slope turn toward #6 passed review.
  The physical hull began turning at 21:12:02.757. The HE launch at
  21:12:07.001 killed #6 on impact. The player killed the hillside #13 at
  21:12:53 and handed off to #10 at 21:12:53.440 within engagement 2.
  The 13-slice, 63.65-degree left turn toward #10 passed chassis review.
  At 21:12:54.326 the actual aim reported `hydraulic_pitch_limit`. The
  controller selected #12 next and three HE impacts on #12 were recorded
  from the same position. The full #13-to-#10 left turn and shot remain
  unverified in that handoff.
- Round 2. The player turned left toward #9 and landed two HE shots, killing
  it at 21:23:01. A later review of #12 remained pending while the atomic
  receipt included a world-blocked point. For #10 the six-slice chassis
  review passed at 21:24:09.453 and the turn began at 21:24:09.474. The
  actual heading changed from -143.928 to -172.354 degrees. The first-trigger
  receipt was `auto_actual_barrel_miss` for the attempted shots at #10.
  These observations distinguish the completed turn from a verified launch.

The team-2 FV215b 183 was #26. At 21:13:14 the line to enemy UDES 03 #9
hit world geometry and at 21:13:16 the engagement handed driving back to
the route with `point_recovery_no_checked_position`. The 21:14:27 clear
penetration evidence was revoked after the muzzle moved 0.20 m. The recheck
hit the terrain and later the player wreck. The same FV hit and killed
enemy UDES 03 #10 at 21:14:07.

Runtime `fa2437530219de2ea68c9fe02bbf6b4453be3c29` passed 1,195 focused
tests covering stationary planning, hydraulic combat and startup, legacy
runtime, support queries, vehicle physics and launch admission. CPython
2.7.18 compiled all 264 client sources. The non-coplanar turn and diagnostic
tests fail on `7471c825`. The midpoint-support test also passes there. The
combined ownership check and the two burst diagnostic assertion failures
were reproduced on the same baseline in the local Windows test environment.

The package is `wot_PR119_fa243753_Windows_2026-11-12.zip`. The new client
payload and staged server files use the runtime commit above. The package
reuses the existing x64 launcher executable. The shipping x86 native source
stamp, the ZIPs, the client bytecode and the installed payload were checked.
The two-round report is
`wot-error-report-20261112-212608-26f4e5af5b4a.zip`. All four session logs
are present and the archive passed CRC verification.

## November 12 follow-up — Siege transition order and hydraulic aim

The travel controller observes a clear trajectory to a current enemy sample
with the existing world, friendly and front-vehicle checks. Two continuous
seconds of clear contact admit the siege request. Automatic combat keeps the
same engagement while the native switch is pending. The gun evaluator and
automatic gun input start checking pitch and yaw once the client observes the
enabled mode and its current descriptor. The protected stationary task and
single-feature control tests cover who may request the mode.

The player gun-angle conversion uses yaw, pitch and roll from one actual
stabilised body observation. Navigation still owns the chassis heading. The
original Redshire cross-slope input produced about `3.18e-5` radians of
spurious pitch when the chassis yaw was paired with the hydraulic pitch and
roll. The complete body transform gives a zero local angle for the reproduced
forward direction.

The hydraulic motion source still tries the strict `1e-7` radian pitch and
correction tolerance first. If all six calls miss it, the smallest measured
error can supply a motion input when the native answer stays within mechanical
travel and both residuals are at most `1e-6` radians. The regression exercises
the `2.272338e-7` radian Redshire residual, a later strict answer and a point
outside hydraulic travel. The existing actual-barrel and first-trigger
checks authorize fire.

With **Collect detailed diagnostic logs** enabled, the report includes the
mode wait, actual aim basis, rounded actuator input and rejected support
samples. The support diagnostic records the five heights already sampled and
the fit residual when available. The support decision still uses the existing
plane fit and tolerance.

Runtime `aa550bfaa626a150e260d3ec8037da4b909984ba` passed 963 tests in 39
isolated files. The three changed expectations reproduce the failures on
baseline `438ec3fb`. The launcher ZIP contains the independently verified
264-module client build `local-qa-siege-order-aa550bfa`. The installed
mod's bytes match the ZIP used in the Windows test.

Windows HD #1513 ran the same Redshire 15 vs 15 scene with player UDES 03
on team 1. The in-battle rack was 13/13/14. At 19:29:13.366 the test
command returned `shell_ready` for HE compact descriptor 3722, slot 2,
with one chambered round and zero reload time. Automatic control resumed
with HE ready at 19:29:14.271.

- At 19:30:14.104 a clear point on #24 admitted siege after 2.005 seconds.
  At 19:30:14.505 the switch was still in progress and the same engagement
  held control. The first actual-body aim sample was at 19:30:16.520 in
  enabled siege. The first HE shot at 19:30:20.583 dealt 166 damage to #24.
  The second HE shot at 19:30:29.572 removed #19's remaining 110 hit points.
- A further entry at 19:31:03.087 confirmed 2.008 seconds of clear contact.
  At 19:31:13.157 the native input for #24 accepted a pitch and correction
  residual of `1.103586e-7` radians. The physical trigger fired at
  19:31:14.742. The server applied 198 HE damage. These three player shots
  each have a matching debit, projectile and server impact.
- The first two engagements still released on
  `siege_stationary_review_stalled` at 19:30:43.520 and 19:30:57.038.
  The sampled support-plane fit recorded five heights and a first
  residual of 0.049437 m. The geometry needed to resolve those specific
  slope waits remains open.

The final report is `wot-error-report-20261112-193338-52da6926c4a7.zip`.
The player's HE rack changed from 14 to 11 and each server projectile
matched its native trigger and impact. The second shot's client penetration
was 458 raw damage. The server applied the target's remaining 110 hit points.
Allied UDES 03 #10 had support-fit and body-observation rejects and died
before it recorded a shot in this round. In the preceding build's
same-scene round #10 had ten server impact receipts. That run already
contained a body-observation reject. The precise cause of the final
round's Bot pause remains open.

The player died at 19:31:21. The launcher deliberately stopped the
session at 19:33:31, accounting for the final worker disconnect. The
four session logs are present and the report ZIP passed its integrity check.
The package for player testing is `wot_PR119_aa550bfa_Windows_2026-11-12.zip`.
[Runtime CI](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/43208959712).

## November 12 follow-up — Empty Bot critical records and siege turn progress

Runtime `e467a85e790d3653b0549a669aa56b26ab1775eb` uses the canonical
empty worker `critical` object as an observed empty destroyed-module list.
Missing records and incomplete nonempty records still defer the projection.
The worker still reads its native support and motion observations.

In the 14:25 report, a clear HE point on #24 moved from 23 m to about
6.5 m away as the target crossed the player's heading. From 14:22:00.036
to 14:22:04.096 the UDES 03 hull turned from −1.44° to −13.93° while the
requested hull heading moved from −2.61° to −52.23°. The historical
minimum error could not recognize the measured turn as progress.
Isolated playback of the three recorded yaw pairs kept the old progress
clock at 216.287 s and renewed the new clock at 220.354 s.
During an active siege lay, the same current clear point can renew the
existing watchdog when the observed hull advances toward the preceding
commanded heading and the command remains in the same direction. Actual
net advance is required. A genuine six-second stall or rotation refusal
ends the lay. The physical trigger checks authorize fire.
The additional turn and empty-record observations use **Collect detailed
diagnostic logs**.

Windows HD #1513 ran the same Redshire 15 vs 15 preset as team 1 UDES 03,
with 29 Bots and a 13/13/14 rack. At 15:09:32 the native `select_shell`
command returned `shell_ready` for compact descriptor 3722, slot 2, with
one chambered round, zero reload time and `can_fire=true`. The same shell
was ready when automatic driving and firing resumed at 15:09:33.

- At 15:10:35.889 allied UDES 03 #10 supplied an empty `critical` record
  during siege. It then laid against #24 and fired at 15:10:37.582.
  Projectile `1:b:10:1` was published and echoed, and the server settled
  a penetration for 422 damage. The archived worker log contains zero
  `worker native critical observation is unavailable` records. Three
  hydraulic body mismatch observations were reported for #10. #10 was
  destroyed at 15:10:52 after combat with #24.
- The player entered siege in episode 1 and tracked the same clear sample
  on #19 for over six seconds. At 15:11:21.703 the recorded turn toward
  the preceding command reduced its remaining angle from 2.059° to
  1.936°. The physical trigger fired HE at 15:11:22.590. The client
  reported 528 raw penetration damage. The server removed #19's remaining
  84 hit points and confirmed the kill. Another HE round dealt 79 explosive
  damage to #28.
  Both auto-trigger receipts match server impacts. The regression
  reproduced the growing-error failure from the preceding report. The
  sampled live turns in this session had shrinking error.
- The player released siege at 15:11:36.524 and 15:11:49.835 on
  `siege_stationary_review_stalled`. The turn watchdog had no active pivot
  in either release. The two positions repeatedly rejected sampled support
  planes with residuals of 0.022377 m and 0.081437 m against the existing
  0.0001 m threshold. The appropriate support representation for these
  poses remains unproved. The player was destroyed at 15:12:08. The
  launcher ended the session at 15:14:15.

The native report is `wot-error-report-20261112-151422-566152f773bd.zip`.
The Windows test ZIP `wot_PR119_e467a85e_Windows_2026-11-12.zip` contains
build `local-qa-siege-pivot-e467a85e`. Both archives passed integrity checks.
The launcher is x64 and the client mod contains 306 stored members. The
two changed client modules and their staged source copies are `bot_binding`
and `combat_stop`.

The new regression tests reproduced the empty-record exception and the
missed physical progress before the fix. The stationary observation keeps
the missing-state and damaged-module cases. The siege regression covers a
clear point whose bearing moves faster than the hull, a real stop and hull
jitter. The 36 isolated player files passed all 916 tests. The three shared
worker and ownership files passed 60 reference tests. The detailed-log
toggle and CPython 2.7 compilation were checked separately.

The pushed runtime passed Bot behavior, native geometry, navigation,
Windows server and Windows editor checks. The full client suite passed
530 of 531 files. The remaining file reproduced the same three Bot reload
assertions and values as baseline `d6d8f34b`. The launcher passed all 49
files. [Runtime checks](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/43174071306) · [Baseline checks](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/43168854396).

## November 12 follow-up — Siege yaw rounding with HE loaded

The diagnostic report `wot-error-report-20261112-124953-978e2610b91c.zip`
captured a clear, mechanically reachable UDES 03 point whose six native
inverse calls left at least `1.0205e-7` radians of yaw error. The motion
source's former `1e-7` radian check rejected the input even with acceptable
pitch and hydraulic correction.

Runtime `e907d09488a80cdc5a454cdcd88a2a8689cceacb` uses a `1e-6` radian yaw tolerance
for the native siege aiming input. Pitch and hydraulic correction use
`1e-7` radians. The motion input carries aiming authority.
Actual barrel, lane, armour and first-trigger checks authorize the shot.
The support-plane review records fit residuals or sampled and predicted
plane values under **Collect detailed diagnostic logs**. It applies the
existing support decision and feeds the original driver.

The Windows HD #1513 test used build `local-qa-siege-he-yaw`, the same
Redshire 15 vs 15 preset, team 1 UDES 03, and a 13/13/14 rack. The launcher
test command received `shell_ready` at 14:20:12.200 with shell index 2,
one chambered round, zero reload time and `can_fire=true`. The client
confirmed HE again after automatic control resumed at 14:20:13.005.

- After 2.011 seconds of route confirmation, siege was enabled at
  14:21:45.861. At 14:21:45.890 the clear point on enemy UDES 03 #24
  published a native aiming input with yaw residual `1.0674e-7` radians.
  The same HE point was accepted at the physical trigger at 14:21:49.485.
  The server settled the shot as a penetration for 460 damage.
- At 14:22:34.279 UDES 03 fired HE at PFM-42 #18 for 406 penetration
  damage. At 14:22:41.648 it used the HE fallback against #24 for 197
  damage. All three automatic HE launches matched server impact receipts.
- The 19 player yaw acceptance records all satisfied the pitch and
  hydraulic thresholds. The 18 support-fit rejects reported residuals
  from 0.0143 to 0.0795 metres. This identifies the sampled-plane fit
  check, with a threshold of 0.0001 metres.
- The player still released engagement at 14:22:05.656 on
  `native_pivot_stalled`, with #24 present, HE ready, and the sampled line
  clear. Its gun was at the yaw stop and the hull turned as the required
  bearing moved farther away. It resumed the route, moved roughly 39 m,
  then confirmed PFM-42 #18 for 2.031 seconds and reentered siege.
- Allied UDES 03 #10 fired eight server-settled rounds, with its last at
  14:24:31. It entered a further engagement at 14:24:48.352, then held
  the same position from 14:24:53 to 14:24:57 while turning. It moved
  again shortly before enemy #27 destroyed it at 14:25:02. The cause of
  the later period without a shot remains open.

The report is `wot-error-report-20261112-142558-89535d27f5a4.zip`. The
player died at 14:22:43.997. The launcher ended the session at 14:25:48,
which accounts for the final `worker_disconnected` receipt.

All 914 tests in the 36 isolated player test files passed. The focused
six-file run passed 175 tests, including diagnostic mode and physical
trigger cases. The same slope rejection emitted a support record only
with the detailed checkbox enabled. All 264 client modules compiled with
CPython 2.7.18. The Windows test ZIP
`wot_PR119_e907d094_Windows_2026-11-12.zip` passed the x64 launcher,
nested archive and 267-source staging checks. The installed mod differs
from `local-qa-siege-r4` in `siege_planning.pyc` and
`stationary_plan.pyc`.

## November 12 follow-up — Bot projectile publication and UDES 03 siege

The 02:40:54 report from the Redshire 15 vs 15 scene contained 1,553 local
Bot rounds across 27 vehicles and zero server Bot projectile terminals. UDES
03 requested siege 11 times against the same PFM-42 after its last shot.

- The worker commits and publishes the first round using the same trajectory
  that passed its trigger checks. Direct fire retains the admitted velocity
  from the engine vector. Artillery retains the already proved dispersed arc.
  The launch identity, shell, muzzle and shot angles still fence the frozen
  record. The server acknowledges and settles each accepted projectile.
- A blocked laying point yields to the remaining review within the current
  siege engagement. Native actuator and firing checks run for each usable
  point. A temporary missing inverse during reload preserves the engagement
  and starts the stall clock from current work once loading finishes.
- After a real release, a new clear point needs two continuous seconds before
  the next takeover. The previous failed point can qualify again after a
  confirmed reopening or a material change in firing geometry. Siege aiming
  and final fire admission still use the native mode and barrel observations.
- The waiting-for-a-new-point and accepted-confirmation receipts are under
  **Collect detailed diagnostic logs**.

### Replacement Windows test package

Runtime `cf111cec6e086fcfae9d73cae58ffa516b42b57e` builds as
`local-qa-siege-r4` in `wot_PR119_cf111cec_Windows_2026-11-12.zip`.
The first follow-up package rejected a valid, certified hydraulic aim if the
unlaid barrel's line was still unknown. The replacement admits the current
stationary plan for laying after the review finishes, skips a currently
blocked point, and keeps the exact pose and physical firing checks.

The replacement was run through the launcher on Windows HD #1513, on the
same Redshire 15 vs 15 preset with UDES 03 in team 2 and a 13/13/14 rack.
The round ended by capture at 04:00:15. The launcher report is
`wot-error-report-20261112-040041-7cd6aef8cded.zip`.

- The worker submitted 282 rounds from 27 Bots. The accepted 278 matched
  the server echo, terminal and visible tracer by actor and shot sequence.
  The terminals include 214 impacts, 64 misses and nine artillery rounds.
  The four other sequences were suppressed after server-confirmed shooter
  death. They are Bot/sequence 1/9, 1/10, 5/3 and 18/8.
- UDES 03 took over after 2.031 seconds of confirmation and entered siege.
  It fired eight automatic rounds with eight server terminal receipts while
  remaining in that engagement. The eighth fired HE at PFM-42 #3 at
  03:58:05.574, penetrated and applied 492 damage. It then resumed the
  route when the review of the next obstructed contact stalled. This round
  had one entry and one exit. The preceding run and the reentry regression
  cover later two-second confirmations.
- All 912 tests in the 36 player test files passed using the repository's
  isolated runner. The 89 shared-owner checks passed on the reference
  backend, as did the diagnostic mode and launcher panel suites. All 264
  client modules compiled under CPython 2.7.18. The package passed x64
  launcher and nested archive checks. It contains 306 stored mod members
  and 267 matching staged server sources.
- The first follow-up CI also flagged three Bot reload cases in
  `test_port_0922_actor_binding.py`. The three assertions reproduce on
  the incoming `da3c8db5` tree. They cover a completed load and fire in the
  same slice, queued-shell promotion and exhausted-stock promotion. The
  full-suite result retains those failures for separate follow-up.

### Earlier runs in this correction

The intermediate Windows run in
`wot-error-report-20261112-032842-2c1315d4984d.zip` recorded 216 accepted Bot
projectiles with matching terminal receipts, including seven artillery rounds.
Four additional local rounds were suppressed by server-confirmed vehicle
death. UDES 03 penetrated PFM-42 #4 at 03:23:54.831 and #3 at 03:24:02.840
in the same siege engagement. A later temporary inverse loss while loading
prompted the final reload and point-retention correction.

The earlier Windows HD #1513 run used `local-qa-siege-r3` at runtime commit
`9223d245b0d0c70479f17c0c55ac9bab12315a2d`. The launcher exported
`wot-error-report-20261112-033432-cb9e72b899b8.zip` after the round ended by
base capture at 03:33:57. The room used the same 29 Bots and player UDES 03 in
team 2 on Redshire, with the 13/13/14 battle rack.

- The worker submitted 313 rounds from 24 Bots. The server acknowledged
  310, and all 310 had a terminal receipt and a matching client tracer.
  Of those, 262 registered an impact and 48 resolved as misses. Two were
  artillery rounds. The remaining three local submissions were explicitly
  suppressed after the shooter had already died on the server.
- At 03:32:39.117 UDES 03 admitted PFM-42 #4 after 2.019 seconds of
  confirmation. It entered siege, fired APCR at 03:32:43.868 and killed #4
  with 110 actual damage. The next target review stayed in the same siege
  engagement through reload. The run later returned to the route after a
  real stall and confirmed a different target before the next siege entry.
  All three player rounds had matching server terminal receipts.
- The four observed route takeovers took 2.001–2.025 seconds. The same
  sample on Bot #9 qualified again only after the hull advanced more than
  nine metres following the preceding stall.

The focused regression run passed 501 tests on the reference backend, and
all 36 launcher testing-panel cases passed. The broader combined reference
run reproduced a pre-existing order-dependent loading snapshot failure.
That case passes in isolation on both trees. All 264 client sources
compiled with CPython 2.7.18. The test package
`wot_PR119_9223d245_Windows_2026-11-12.zip` passed x64 launcher, nested
archive, 306 stored mod member and 267 staged server source checks.

## November 12 follow-up — Redshire moving battle, artillery, and siege

### Test setup

In the launcher Test tab, select **Mobile combat test (15 vs 15)** and start single player. Select a vehicle and the listed gun in the garage. The room places the player in its matching slot, with 29 Bots filling the other slots. The scenario sets the in-battle ammo rack for both player and Bots. It uses the stock gun capacities and leaves the garage rack in place.

When the waiting room carries a stale **Starting** message after changing vehicles between rounds, leave it and join again before starting the next battle.

| Vehicle | Per team | Gun | Rounds by shell type |
| --- | ---: | --- | --- |
| PFM-42 L-120 | 4 | 20 mm pvlvkan m/40 | AP 80, APCR 80, HE 80 |
| AMX ELC | 4 | 90 mm D. 914 | AP 12, APCR 12, HE 12 |
| UDES 03 | 2 | 10.5 cm kan UDES 03 | APCR 13, premium APCR 13, HE 14 |
| FV215b (183) | 1 | 183 mm L4 | AP 6, HE 7, HESH 7 |
| Type 4 Heavy | 1 | 15 cm 45 41st Year Type | HE 20, premium HE 20 |
| O-Ho | 1 | 15 cm Howitzer Type 96 | AP 20, HEAT 20, HE 20 |
| Object 261 | 1 | 180 mm B-1-P | HE 9, premium HE 9 |
| Bat.-Châtillon 155 58 | 1 | Canon de 155 mm | HE 18, premium HE 18 |

The Redshire preflight used the previous Windows HD #1513 package. The 20 mm PFM-42 drove and fired on the existing map routes. Object 261 landed a shell on the central moving line and killed two PFM-42s in the same splash. Bat.-Châtillon fired from the western rear position and received server impacts. The scenario splits the four PFM-42s on each team between the east and west corridors. AMX ELC runs the west and centre routes. UDES 03 uses the east ridge and the two Japanese heavies use the centre. All 12 scene route assignments were checked against the current Redshire navigation graph. The scene uses the existing route, waypoint, driving and capture contracts.

The Object 261 retest assigned it to the east low ground near `(185, 468)`. The native arc check reported a ridge strike near `(244, 410)`, so the scene now uses only the existing rear and west parking areas. The ordinary map profile retains its parking areas.

### Changes and receipts

- The November 12 report `wot-error-report-20261112-000853-9bc3d539053d.zip` showed a fresh 2.039-second confirmation after an AMX ELC kill with another enemy still visible. Combat now passes to an eligible remaining enemy in the same engagement. First contact and reacquisition after genuine release use the existing two-second confirmation. The no-HE cooldown remains in force.
- The same report showed a completed UDES 03 siege switch followed by 2 minutes 41 seconds with no movement until manual input. The stationary review repeatedly restarted on small native pose changes. The follow-up report `wot-error-report-20261112-015258-102d2a503637.zip` also showed nearby moving actors repeatedly invalidating completed terrain checks. The stationary planner anchors settled hydraulic observations at its existing position tolerance, retains completed static arc work, and checks actual nearby vehicle positions again before a planned turn. Exact native movement and trigger checks still run. A stalled review hands the hull back to the original task.
- Ordinary ammunition candidates now use ascending penetration, then ascending listed damage within the same penetration. In an active engagement the mounted ammunition, current-target HE comparison, and last physical trigger still govern when the next type can load.
- The v1.1.1 artillery result rule counts two settled rounds with neither an enemy direct hit nor enemy damage. A direct hit or damaging splash clears the miss streak. The alternate HE uses the existing native reload owner, at the full-magazine boundary on a clip gun. Regular HE reloads after two fired backup rounds on a single-shot gun or one completed backup magazine. A change of target or a position shift beyond the original tolerance clears accumulated misses. Projectile and settlement receipts use the server's shooter identity for both player and Bot.
- In the follow-up report a Bot fired AP at the end of a magazine, while the same checkpoint already described its loaded shell as HE. The server rejected that shot. The worker now publishes the consumed AP and the next HE separately until the full load completes. The server still validates both inventory conservation and the physical firing shell.
- Artillery target review, unfinished stationary review, and ambiguous ammunition transitions gain detail only when **Collect detailed diagnostic logs** is selected.

### Windows HD #1513 verification

The Windows package is `wot_PR119_4cb1b894_Windows_2026-11-12.zip`, with runtime `4cb1b8949be8b97e9c35fd86deaa00c58bbd7399` and build identity `local-qa-mobile-r7`. Its SHA-256 is `973277953E981F369DAA8312E2BD2C6901D7DA8A490E53A3C9614E5B980389BD`. The x64 launcher was rebuilt. The native client binaries and map data match the previous package byte for byte. The nested archives passed CRC checks. The game mod passed the stored-member validator with 306 members and 264 CPython 2.7 modules, and 267 staged server sources matched the worktree.

- In the UDES 03 retest before the scene-only parking adjustment, it had a 13/13/14 rack. Siege was confirmed by 01:56:38.708, and its first shot reached the server at 01:56:45. The engagement remained owned while the selected ELC changed from Bot 6 to Bot 5. UDES 03 fired six rounds, recorded 1,791 damage and two kills, and later drove again without manual movement. The six launches had six terminal receipts. The Bot worker started 29 vehicles with the specified fittings, including all eight ELCs, and the server recorded a capture result. The report was `wot-error-report-20261112-020555-b1506e3a7358.zip`.
- The final package ran Object 261 at 9/9 from the rear parking area near `(-58, 470)`. All four automatic shots matched server launch and settlement receipts. The first three were direct hits. The fourth had no direct hit but applied 525 splash damage, so regular HE remained selected. The server ended the match by capture at 02:12:10. The report `wot-error-report-20261112-021241-410834b424b2.zip` contains the 29 Bot racks, four Bot target handoffs, and no repeat of the Bot shell-boundary rejection or logged player/worker traceback.
- The final round did not produce two qualifying artillery misses or a Bot artillery projectile receipt. The native shot and ammo receipt chain was observed for the player. The regression cases cover both the single-shot return and the Bat.-Châtillon's physical magazine boundary. The report retains the Bot arc review and fire-gate observations for follow-up.
- The focused regression suite passed 572 cases, using the reference simulation backend where the external Python test runner needed it. The launcher suite passed 325 of 331 cases with six environment-dependent skips. All 36 testing-panel cases passed, including the unchecked-diagnostics scenario. The live rounds used the Windows native game and worker.

## November 11 follow-up — obstructed points, capture aiming, and high-penetration reload

### Reports reviewed

- The PFM-42 L-120 report, wot-error-report-20261111-205753-e481bcdbb401.zip, records its last HE round at 20:56:38.165. It then repeatedly refuses the same sample on enemy 14 after the near-world check of the sampled projectile trajectory, although the centre ray passes. The APCR selection at 20:57:31 was manual, after about 53 seconds without a shot. The refusal continued after the APCR load completed.
- The follow-up archive wot-error-report-20261111-210357-e481bcdbb401.zip also contains the AMX ELC 90 mm round. The two-second route handoffs worked early in that round. Later the vehicle registered capture and stayed inside with no shot. The firing policy had a visible point with an ideal clear line, but the yaw check lacked a stationary projection and the protected capture order could withhold the alternate target from hull aiming.
- The local intermediate build local-qa-36695638 identified the missing player critical-device observation and exposed a second circle problem. In wot-error-report-20261111-221954-ffc8a6dbf7f8.zip, the AMX ELC alternated between enemies 10 and 12 from 22:16:08 to 22:16:39, with opposite turn requests, zero throttle and zero shots. The last AP shot was at 22:15:50.400. Capture still completed at 22:17:44. The same archive records a manual APCR reload while 10 of 20 rounds remained in the PFM-42 clip. No low-penetration shell had been queued, and the native reload kept APCR.

### Changes

- The first confirmed near-world scatter refusal excludes that exact shell, vehicle and sample from both penetration and blast selection. A bounded read-only recheck uses the same scatter draw and actual ray probe. A clear result reopens the point. Other points on the same vehicle take priority before the penetration sweep advances to another vehicle. HE stays on the held vehicle, checks clear penetration points, then ranks blast damage there when needed.
- Capture owns the parked position while the selected alternate target can use existing native hull aiming. Collision checks and the capture-circle boundary apply to each actual pivot. The protected turn keeps its target at the front of the review while observations refresh. A dead or unusable target can yield to another target. A stalled or refused rotation yields through a bounded retry. Stationary aiming reads the accepted local damage snapshot or the live entity devices before the first damage payload.
- A high-penetration clip with stock can queue an automatic low-penetration return at its last physical trigger. A single-shot gun needs one prior committed high-penetration round and the next actual firing edge. A refused or aborted trigger retires its temporary request. The current low-penetration failure evidence can still defer return. HE penetration clears the fallback streak, and an HE clip follows its existing end-of-clip rule.
- The route-to-combat gate still requires two continuous seconds of an actionable point. The changes enter through combat and loading, using the existing route, waypoint-arrival and capture-registration interfaces. Additional evidence for a missing stationary projection, a broken confirmation, route release, blocked-point reopening and an unsuccessful circle turn is recorded only with detailed diagnostics enabled.

### Windows HD #1513 verification

The tested archive is wot_PR119_cf1a01c3_Windows_2026-11-11.zip. It uses runtime cf1a01c37e792d0a518fb0898376e28eb086d607 and build identity local-qa-cf1a01c3. The SHA-256 is AD6B0C8FE8E569DBA46B420FFFECDCD7FA24C16EDCEA01709FB1A45C83E333CD. The QA bundle reuses the previous Windows launcher and native payload with the current gameplay bytecode. The outer and nested archives, x64 launcher and all 263 CPython 2.7 client modules were verified.

- In Mittengard team 2, with the stationary-target preset and detailed diagnostics enabled, AMX ELC 90 mm recorded two route handoffs at 2.042 and 2.008 seconds while the gun was still unaligned. After manual APCR selection through the local test control, the first APCR shot reloaded APCR. The second APCR shot at 22:24:56.614 started an automatic AP reload.
- Capture registered at 22:25:37.420. Seven AP shots during capture matched server projectile receipts. The capture rows kept zero throttle and one enemy, bot 3, when they named a gun target. The server recorded a capture win at 22:27:17. The final report is wot-error-report-20261111-222725-03b6e2be6619.zip. All 14 shots matched the server and the foreground and worker exception trails were empty.
- The same report did not encounter the original near-world scatter refusal or the exact two-target circle oscillation. Deterministic native-geometry regressions exercise the first refusal, same-vehicle alternatives, obstruction clearance and the opposing-target turn. The opposing-target test failed on the previous implementation before passing with target retention.
- The local test run passed 42 files. One worker case requires the matching simulation backend, which the external Windows Python process lacked. That worker case and the shared HE, physical-blocker and recovery suites passed on the reference backend, 40 tests in total. The packaged native client and worker ran the live match above.

## November 11 follow-up — current-target HE and front-vehicle admission

The L-120 TD round in `wot-error-report-20261111-173700-f67e91ff6225.zip`
used `colorfulmeans-42987574283-1`. Between 17:34:19.879 and
17:35:10.772 the AP clip did not fire. The player repeatedly handed the
hull to combat targeting enemy 14 with a still-obstructed ray. The report has
50 `auto_front_vehicle` refusals in that round, including blockers 10,
11 and 13. The player learned of those contacts at native trigger
admission, after combat had already taken the hull.

- Mounted player HE checks penetration points on its held vehicle and
  skips obstructed points. It uses the first executable penetrating
  point. After all available points fail penetration, it compares
  estimated non-penetrating blast damage on that same vehicle and
  rechecks the highest-scoring usable point for the trigger. An
  incomplete comparison can only pre-aim. Ammunition return remains
  driven by committed rounds and the native clip reload.
- Before a point can qualify for route-to-combat admission, the intended
  trajectory checks which hostile hull it would strike first. A
  foreground vehicle excludes that point and interrupts its attack
  evidence. A continuously usable ray qualifies after two seconds, and
  the real barrel or hull can finish laying after handoff. The final
  native shot still requires its independent physical check.
- A confirmed wreck, friendly vehicle or world obstruction still enters
  the existing finite recovery for owned combat. The driver, waypoint
  arrival, route selection and capture navigation retain their existing
  implementation. The detailed diagnostic option records front actor
  IDs and the progress and scores of the held vehicle's HE comparison.

The regression suite exercises a moving front hull, a clear alternate
point, the two-second reopen boundary before physical alignment, a later
penetrating ordinary-HE point, and unequal native blast scores. Its HE
cases also cover obstruction, target retention and the distinction
between potential penetration and non-penetrating blast damage.

### Intermediate Windows HD #1513 verification

[Windows build 43004424175](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/43004424175)
packaged runtime `0f959debb5153c8093de7baa66bb1cd6fe4147c0`.
Artifact `13847748397` has build identity `colorfulmeans-43004424175-1`.
The downloaded ZIP, embedded client ZIP, x64 launcher and 263 packaged
Python 2.7 modules were independently checked before the launcher was
used to install and run the build.
[Tests 43004427958](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/43004427958)
passed at the same runtime commit, including the navigation, bot,
client, Windows launcher and native geometry jobs.

- L-120 TD / PFM-42 with `_20mm_pvlvkan_m_40` and 80/80/80 stock,
  Mittengard team 2, stationary-target preset. The first handoff took
  2.021 seconds with the gun still unaligned, and the first AP round
  followed 1.705 seconds later. The detailed records excluded samples
  on enemies 2 and 14 when the intended ray met enemies 5 and 7 first.
  Another AP round followed the last such record in 1.448 seconds.
  The report contains one route handoff and zero late front-vehicle
  refusals.
- In the same round, the launcher test control loaded ordinary HE with
  automation released. Automatic fire evaluated all nine eligible
  points on enemy 7 before fallback. It used different points on that
  same vehicle through the 20-round clip. The next clip used the
  lowest stocked penetration shell, APCR, since AP was exhausted.
  The 138 committed projectiles all matched server shots. The visible
  and worker exception trails were empty. Report
  `wot-error-report-20261111-185105-7d3070a546b4.zip`.
- Škoda T 24 with `_75mm_Skoda_A18` and 17/17/16 stock on the same
  map and preset reproduced a remaining HE ownership loop. It made
  five confirmed handoffs to enemy 2 before the first shot. Immediately
  after handoff, the running penetration review stopped publishing its
  still-clear HE contact, so the existing opportunity-loss grace period
  expired during the sweep. The same battle later compared four clear
  points on enemy 2, chose sample 8 with an estimated blast of 69 over
  the other three at 0, and fired that point twice before returning to
  AP. Report `wot-error-report-20261111-185617-4df4afa1ed92.zip`.

The follow-up lets the current, unblocked HE contact continue to support
the already confirmed stop while the same target is being reviewed.
It still needs the complete ranking to fire a fallback shot. A fresh
blocked line cannot retain that proof. The first follow-up still lost
the opportunity during small source changes in
`wot-error-report-20261111-191311-dcf5614e43fa.zip`. The earlier armour
failure was valid within the ranking tolerance, so blocked points took
both foreground probes while the clear point's exact lane expired.
The final change gives that point the first available foreground probe
and applies the normal obstruction checks to the refreshed ray. The
native-observation regression reproduces that release and requires one
handoff followed by a real HE launch with the completed ranking.

### Windows retest of the HE handoff

`wot_PR119_1d45aa54_Windows_2026-11-11.zip` uses runtime
`1d45aa54a8809d2affd637393214e968bbd10270` and build identity
`local-qa-1d45aa54`. The ZIP reuses the verified x64 launcher, server
and native resources from Windows build 43004424175 with the updated
CPython 2.7 client modules. The outer ZIP, inner client ZIP and mod
passed archive checks. The complete inventory of 263 client bytecode
modules matched the runtime source. The acceptance run used a fresh
extraction of this same ZIP. [Runtime Tests 43010296857](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/43010296857).

The same T 24, map, side and stationary-target preset reproduced
foreground obstructions on enemy 2. The report shows one HE handoff
for that enemy after 2.021 seconds of confirmation while the gun was
still unaligned. Enemies 3 and 5 obstructed eight of the nine samples
at fallback selection. The gun used the remaining sample, 5, for
both HE shots and returned to AP. The first HE shot followed handoff
in 4.891 seconds. All 12 local launches matched the server, with no
late front-vehicle refusals and empty visible/worker exception trails.
The later handoff in this capture was for enemy 7 with AP.
Report `wot-error-report-20261111-191748-abfd2a01065b.zip`.

### HE return after two consecutive fallback rounds

The return to the lowest stocked penetration shell now counts
committed HE rounds by the mode of their accepted trigger. A
penetrating HE round resets the consecutive fallback count. A
single-shot gun uses the lowest stocked penetration shell for the load
after the second consecutive fallback round. A clip or burst gun
finishes the mounted clip once that threshold is reached. A still-valid
complete failure certificate for the lowest penetration shell defers
the change, and stock exhaustion still selects a stocked shell.

The last native trigger can stage NEXT for its confirmed HE fallback
mode, and the native gun promotes it only on the actual reload
boundary. A refused trigger releases that provisional setting and
spends no round. An existing manual selection retains its own
ownership. The code uses the current trigger and committed burst
receipts with no extra armour scan at the trigger.

Regressions exercise a penetrating HE round between fallback rounds,
continued penetration across a full clip, two fallback rounds
followed by penetration in the remainder of the same clip, a refused
second fallback trigger, actual burst tails, and the cached complete
failure proof that defers the lowest-shell return.

The delivered `wot_PR119_845d87b3_Windows_2026-11-11.zip` contains
runtime `845d87b378be5a26886c285c2e7cd5e1281bbc8a` with identity
`local-qa-845d87b3`. It uses the same verified x64 launcher, server and
native resources. All 263 bundled client modules matched the runtime
source. All 39 local player-control and report-regression test files
passed. [Runtime Tests 43012626933](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/43012626933).

The T 24 acceptance run started from a fresh extraction of that ZIP
with the same stationary-target setup. The log excluded the blocked
samples on enemy 2 and compared the four clear points. Sample 8 won
with estimated blast damage 80. The other three scored 0. Both HE
rounds used sample 8. The first trigger kept HE with zero preceding
fallback rounds. The second trigger had one prior committed fallback
round and began the AP reload after its own commit. The third
projectile was AP. All 16 local projectiles matched the server, and the
visible and worker exception trails were empty. The capture contains
no repeated HE takeover and no late front-vehicle refusal.
Report `wot-error-report-20261111-193538-ba5271e3f0c1.zip`.

The first PR test run exposed a wall-clock dependency in the 141918
wreck regression. A slower runner paused during penetration review.
The fixture now uses a repeatable native work clock to reach a
partial blast comparison in the first callback, before admission.
The route, turret, native reload, no-fire and wreck evidence
assertions still run through the same production code.

## Follow-up for the 15:47 T 24 report — native fire receipts and ammunition return

The single-shot Škoda T 24 report `wot-error-report-20261111-154736-4f1e0a10cc53.zip`
ran `d5a9ff9f` / `colorfulmeans-42955381063-1`. It first handed off
at 15:42:33.438 and fired at 15:42:53.357. It recorded 21 front-vehicle
refusals and 21 native calls without a receipt. The stock HD #1513
`PlayerAvatar.shoot` starts its acknowledgement timer and its two-second
gun-command deadline after the local mailbox returns, including after a
refusal. The old rejection cleanup cancelled the timer alone. The
new cleanup restores the pre-call deadline for that same rejected
mailbox, fenced to the Avatar, generation and local projectile sequence.
Exact CPython 2.7 bytecode inspection and a regression cover both waits.
The detailed diagnostic checkbox adds the early missing-context reason,
same-point refresh refusal and stock gun/HUD state for a silent return.

- Ordinary player route acquisition requires two seconds of continuous
  attackable evidence. The no-HE handoff starts its independent five-second
  cooldown. The change is at the existing combat admission boundary.
- The five whitelisted HESH pairs review the held target's penetration
  points and take its first executable point. A completed failed HESH
  review uses one fallback point on that target. Ordinary HE uses a
  single point for both its penetration trial and fallback.
- High-penetration and HE single-shot loads queue the lowest stocked
  penetration shell for the reload after two committed rounds. Clip
  and burst guns change at the native full reload after the current clip.
  Existing, still-valid complete negative evidence for the lowest shell
  defers that return. The next load uses current cached evidence and the
  existing geometry tolerance. It issues no fresh armour queries at
  the trigger. An empty stock or a complete current-shell failure can
  still select a replacement before the quota.

### Windows HD #1513 evidence

[Windows build 42987574283](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/42987574283)
built runtime `3dc4132c72e5e6c7a3f7207545aa3983ae53cc3b`.
Artifact `13841156147` carries build `colorfulmeans-42987574283-1`.
An independent download passed all ZIP checks, x64 launcher inspection
and the comparison of 263 packaged Python 2.7 client modules with the
runtime source. The following sessions used the downloaded launcher.

- T 24, `_75mm_Skoda_A18`, 17/17/16, Mittengard team 2. After a slow
  opening around parked allies, the first qualifying handoff completed
  in 2.005 seconds and led to an AP launch 3.424 seconds later. The
  report contains 38 matching local and server launches and eight
  physical front-vehicle refusals. The first refusal at 16:48:35.033
  reached the next native check at 16:48:35.391. The next committed AP
  shot followed at 16:48:40.970 after further blocked/pending points.
  No attempt returned without a receipt in this capture.
  Report `wot-error-report-20261111-165102-bd0400ab00e0.zip`.
- T 24, same gun and stock, Mittengard team 1. The native test command
  loaded APCR while control was released, then the normal control loop
  admitted after 2.020 seconds and fired after another 0.637 seconds.
  The actual sequence was APCR, APCR, AP. A second control activation
  with HE produced HE, HE, AP. The two HE launches both used target 24
  and sample 0. All six were received by the server.
  Report `wot-error-report-20261111-165723-e79f8ba283bb.zip`.

- AT 7, `QF_6_pounder_Mk_V_AT`, ten rounds per clip and 40/40/40
  stock, Mittengard team 1. Route confirmation completed in 2.023
  seconds. The native APCR launch followed 2.462 seconds later.
  The server recorded ten APCR rounds before the reload and one AP
  round from the next clip. The capture ends after the test stopped
  automatic control. Report `wot-error-report-20261111-170514-b9a35684ac43.zip`.

The visible and worker exception trails contain headers only in all
three captures. The Windows battles exercised the ordinary HE and
penetration return paths. The five HESH identities, the scoped fallback
and the expiry of the lowest-shell failure proof were exercised by
the native-observation regressions. The first full CI run found two
files that still expected the old five-second route handoff. The
follow-up adjusts those fixtures and preserves their control and
capture assertions.

## Follow-up for the 11:28 AT 7 and 11:44 Škoda T 24 reports

Both reports identify `5d82c2b2` / `colorfulmeans-42894631616-1` and
record zero player launches. The ten-round AT 7
`QF_6_pounder_Mk_V_AT` in
`wot-error-report-20261111-112828-ef1151939b8a.zip` had a clear
penetrating ray for enemy 23, sample 5, which still needed a hull turn.
The last route receipt recorded 0.557 seconds of confirmation. The
single-shot turreted Škoda T 24 in
`wot-error-report-20261111-114425-6fa3861491cd.zip` had a clear,
penetrating and mechanically reachable AP point on enemy 23, sample 7,
at 11:44:00. Both switched to automatic capture travel before the
five-second confirmation could complete. The travel-mode transition
suspended combat review in both reports.

On a moving source, the mounted-shell firing sweep repeatedly revisited
the first obstructed contact as the exact muzzle changed. The existing
bounded foreground review now rotates across mounted-shell points before
movement admission, with the current positive ray first on the next
observation. A clear, penetrating ray can qualify while its hull still
needs to turn. Automatic travel to the capture circle participates in
the same confirmation, retaining the original destination up to
handoff. The five-second gate and native firing checks apply at their
respective stages. The detailed checkbox records each sample's mechanical
result and stationary projection reason.

Full control-loop regressions use a ten-round limited gun and a
single-shot turreted gun behind an obstructed nearer enemy. They require
the original travel order during confirmation, one combat handoff after
five seconds and a real native AP launch after aiming. A capture-route
case crosses from its authored route into capture travel during the
same confirmation while the tank remains outside the circle.

## Follow-up for the 02:25 AT7 report — mounted shell and same-target points

`wot-error-report-20261111-022506-022abba6ab9f.zip` showed an admitted
engagement with ten AP rounds remaining and no launch during a 46-second
hold. Native first-trigger admission identified hostile actor 1 in front of
actor 3 on several separate samples. A timer let the same blocked sample
return to the front of the old global review even while the blocker remained.
The report also showed a grounded final route-circle observation during
combat ownership followed by a return to its centre on handoff.

- The ordinary foreground gun opens a pass with its retained eligible target
  or the existing nearest-visible ordering. Ties use nominal armour and the
  existing stable actor key. It inspects the mounted penetration shell one
  target at a time, skips obstructed samples and consumes the first current
  executable point. A front contact is recorded against its obstructed sample
  and geometry. Native first-trigger admission still checks the live barrel.
- A completed mounted-shell pass qualifies the next stocked higher penetration
  shell and permits a native whole-clip reload. Exhausting those roles selects
  HE on the last target. Current HE uses one sample for penetration and its
  contact fallback. A fired HE round or the last round of its clip queues the
  lowest stocked penetration shell by inventory alone. The physical burst
  and manual ammunition setting keep their existing ownership.
- A no-HE release starts a five-second cooldown from the actual handoff. A
  fresh continuous attackable observation can accumulate in parallel on the
  original route. A grounded entry into the assigned terminal disc is recorded
  while combat owns movement. Authored route data, intermediate arrival
  checks, base occupancy and the underlying driver remain separate.
- The ordered policy applies to ordinary player-controlled guns, including
  fixed and limited traverse. Worker, artillery and native siege actuator
  paths retain their existing policies. Analytic regressions cover exact
  launch, native ammunition input, trigger tails, route inputs, and real
  motion invalidation alongside negligible source settling.
- The existing detailed-diagnostic checkbox enables `ordered_attack`
  records with loaded shell, target order, completed count, selected sample,
  proposed shell and the current target's point verdicts. These records help
  separate missing native geometry, mechanical restrictions and obstructed
  points in a fresh Windows battle.

The first #1513 preflight used the team 2 east route in the same Mittengard
stationary-target scene. The exported report `wot-error-report-20261111-042019-0aa0ba72934c.zip`
records eight AP and one HE launch. When actor 2's points 1, 2 and 4 were
obstructed, the next committed AP shot used point 5 on actor 2. The later
HE fallback fired point 0 on actor 9, and its native reload mounted AP.
The follow-up retains the earlier out-of-range review receipt without
granting firing or movement permission. It also distinguishes the fired
shell from the shell mounted by the same trigger's reload in the detailed log.

## Follow-up for the 23:53 AT7 report — circle handoff and current shot

The report `wot-error-report-20261110-235323-94c3a3f842a5.zip` identifies
`ef5b7cca` / `colorfulmeans-42842677225-1`. It exercised the five-second
route gate and a committed AP shot after manual HE-to-AP. HE stayed at ten
rounds during a roughly 51-second engagement despite verified aim and
permissive orders. Capture scoring began at 23:51:24, the original route
resumed inside the circle at 23:51:39, and the vehicle held near the end of
the lane at 23:51:44 without a firing target. The capture hold itself was
registered at that stop.

- The shared planner records actual circle occupancy independently of
  combat's movement lease. Eligible route orders carry the capture objective
  so each binding can accept entry from its current grounded pose even on
  a cached order. The circle hold owns translation and leaves the existing
  gun handoff available. A blocked initial hint cannot veto travel from a
  completed route terminal outside the circle. Actor-local circle entry
  constrains the accepted ordinary order after mission selection, so it
  cannot create a new mission or displace a controller-owned task.
- The mounted shell takes a still-valid selected or cached executable point
  before issuing new point queries. NEXT's bounded preparation runs after
  current-shot control during the reload before the final in-clip trigger.
  A ready gun uses the ordinary fair background pass. The last trigger
  consumes a prepared plan, with
  existing ranking tolerance for an already accepted queue and live lane
  and domain checks. The existing native launch admission proves the shot.
- The launcher checkbox **Collect detailed diagnostic logs** explicitly
  enables the new `BATTLE REVIEW` stages for direct-fire gates, trigger
  context and native submission, last-trigger NEXT, current-point
  invalidation, and capture handoff. The checkbox is independent of other
  settings that enable general diagnostics. Records reuse observed facts,
  summarize repeated reasons, and share the existing review limits.
- The regressions compare actual drive commands with and without fire,
  require forward travel in the clear-route fixture, and exercise a living
  enemy, the real five-second dwell, entry on a cached route order, and a
  subsequent committed shot at zero throttle. The tests also cover cached
  green-point priority, an expired NEXT plan without trigger-time scanning,
  an HE magazine into AP, manual HE-to-AP, and diagnostic opt-in.

On Windows #1513, enable the checkbox before launching. Recheck the AT7
entry and parked fire, first HE launch, and the final round of a cassette.
Export the report after the match. Use the direct-fire and NEXT stages to
identify the missing native HE step and distinguish load ranking from
current-shot refusals. The current penetration-cache motion envelope awaits
measured deltas from that report. The PR identifies the verified build.

## Follow-up for the 22:01 AT7 report

The report \`wot-error-report-20261110-220155-71db166b8729.zip\` identifies
\`3c6deb7e\` / \`colorfulmeans-42817074658-1\`. Its AT7 stayed at the same
horizontal position from 21:58:31 to 21:59:33 while the shared engagement
episode went from 9 to 369. Actual commands alternated route turn -1.00 and
combat turn about +0.65. A briefly clear ray could start laying with unknown
armour. The next blocked ray returned to the route and the following clear
ray recreated the pivot. The early route-only collision wait is separate.

The last HE round produced \`higher_rank_pending\` (2/14 current HE-rank
checks) followed by a native same-shell reload. NEXT was empty in all 22 HE
status samples. The HE phase recorded 1,510 source-proof revocations. A
manual CURRENT change later loaded 10 AP rounds, but the preceding HE
fallback phase left the gun in \`he_damage_comparison_pending\` after reload.

### Contract and implementation

- A normal player-controlled automatic route remains the movement owner
  until one enemy has a proved opportunity with the current shell for five
  continuous observed seconds. An invalid, absent, or changed opportunity
  resets the timer. The timer also resets after a gap longer than 0.75 s.
  Current HE contact must satisfy the existing HE fallback law. A verified
  stationary projection can qualify a limited traverse point. An in-motion
  hull-lay candidate may also qualify from a clear ideal ray and a confirmed
  plate or the legal one-point ordinary HE contact. The ordinary native
  actuator still checks each physical turn.
  A clear ray with unknown armour, or a translated line preview alone,
  grants no route takeover. Worker tactics, explicit travel/capture and the
  separate hydraulic siege request/echo protocol keep their existing scope.
- For an admitted route-derived pivot, brief observed lane blockage freezes
  the turn and removes fire permission. After one second of lost opportunity
  the route resumes. Reentry requires a new full five-second observation;
  an unchanged failed rotation or stalled lay cannot repeat from the same
  location. The existing six-second mechanical watchdog still runs while
  checking the lane and only actual turn progress refreshes it.
- NEXT keeps completed ranking evidence anchored to its measured geometry.
  The experimental limits are up to 0.20 m of source/target movement (stricter
  near the target), 0.5 degrees of target/component rotation, and 0.15 m/s
  change in target velocity. Changes in weapon, target geometry/armour
  identity, scene, or a relevant moving blocker invalidate the corresponding
  evidence. A known failed plate or a static world hit can retain its rank
  outcome across traffic changes. Unchecked/blocked armour does not qualify
  global HE fallback. Tolerant NEXT observations are kept out of the exact
  physical failure diagnostics. The winning point is freshly checked before
  queuing NEXT, and current aim/fire still uses exact geometry and the
  original native shot-admission checks. No query quota is increased.
- A real ammunition change clears the previous shell's fallback and lay
  retry state. Queuing a future shell or continuing a same-shell reload does
  not reset the current shell phase. NEXT remains independent of the
  current clip and keeps HE penetration, AP, higher-penetration, HE fallback
  order. An unfinished ranking grants no current clip unload authority.

### Verification and native acceptance

The report regression exercises a real authored route through the five-second
gate, clear/blocked alternation, a sustained limited-traverse opportunity,
a full ten-round HE clip with source jitter and actual AP reload, and a
manual CURRENT HE-to-AP input followed by the actual AP launch. Controlled
queries also verify expiry beyond the ranking envelope and the requirement
for fresh winning-point proof. Existing downstream fixtures that assume an
eligible engagement isolate the route-dwell decision in their setup; the
report and embedded ownership regressions use the production threshold.

On Windows #1513, compare a brief spot with a sustained attackable point on
the same AT7 opening. Check that brief peeks preserve route direction and a
stable contact takes the hull once. Repeat at a wall and with an intervening
friendly, then let one HE cassette finish and separately switch manually to
AP. The PR delivery header identifies the exact CI run and Windows package.
All lower-level driving, traffic, navigation, route, physics, and collision
files are outside this change.

## Live-report continuation: implemented and locally verified

The user's `wot-error-report-20261110-184606-069fba6421d8.zip` rejects the
in-battle completeness of the previous delivery. Its installed and bundled
build is `colorfulmeans-42796652971-1`, the actual `2f8db7b6` PR head, not an
older package. The current continuation starts from that exact remote commit.
The prior verification results below remain historical evidence, not proof
that the reported control and HE failures are fixed.

The reviewed report and production-order reproductions identify three issues:

- An unchecked blocked-point recovery can first take the hull, face the
  enemy, fail and release the route. A route-only yaw change can then admit
  the same failure again. Opening-route controls alternate between opposing
  turns even though the original driver and route laws were not edited.
- A valid limited-traverse native hull lay can be replaced by a candidate-less
  stationary-review wait. Exact physical-source changes invalidate evidence;
  review then freezes the admitted hull instead of continuing the same lay.
- Loaded ordinary HE contact review receives only the budget left by repeated
  penetration review. Current-source jitter can retire background contacts
  before consumption; even a completed historical coverage count is not a
  current executable contact.

The user has now authorized implementation, independent review, original-PR
update and a fresh Windows test package after reading the handoffs and dialog.
The controlling rules are:

1. Loaded HE reviews current HE penetration, then its legal HE fallback,
   before AP and higher-penetration alternatives. Ordinary HE penetration and
   fallback share one stable sample per target. Whitelisted full-validation
   HE keeps its existing point domain. Non-HE selections use the ordinary
   HE-penetration, AP, higher-penetration, final-HE-fallback ranking even when
   the physically loaded shell is the higher-penetration one.
2. Validation order does not grant a new unloading authority. Current valid
   rounds/cassettes and accepted trigger tails retain their existing ownership;
   independently reviewed NEXT chooses the subsequent load. Loaded HE cannot
   be discarded just because a different shell has a better NEXT plan.
3. A proved legal current ordinary-HE contact can execute without waiting for
   unvisited or pending competitors. Completed usable candidates remain
   damage-ranked. This supersedes historical wording which makes a complete
   all-enemy HE comparison a prerequisite for ordinary CURRENT execution;
   it does not remove the independent NEXT or SPG validation requirements.
4. Scheduling progress and point intention survive exact proof refreshes.
   They are not negative-armour certificates, movement permission or fire
   permission. Current geometry, ammunition and native first-edge checks stay
   strict; work quotas and the penetration threshold are not increased.
5. Before initial recovery takes a route-owned hull, it needs a current
   executable point, a justified native stationary lay, or a concrete checked
   same-point recovery destination. The existing native siege mode-entry
   protocol remains a separate, narrow authorization; it cannot grant a shot
   or an unchecked relocation. A blocker or pending probe alone cannot stop
   or steer the vehicle. Relevant changes may schedule another check; only a
   newly proved action, not a yaw threshold, admits another episode.
6. An admitted same-point native lay continues through planning waits using
   the original live actuator and collision checks. Manual/task/capture
   restrictions, identity loss, actual completion and real lack of progress
   remain terminal boundaries. A stale steering value is not replayed.
7. Friendly line obstruction joins the same point-bound recovery. Its old
   independent side-choice, arrival-success and retry owner must not survive
   as a fallback. Physical ally collision and firing-safety checks remain.

No driver gain, steering speed, authored route, navigation law, damage model,
eight-second penetration search, extra controller, main merge, tag or release
is authorized. Modified regression expectations must name the superseding
rule; old-source failures and final-tree results are recorded separately.
Implementation and independent cross-module review are complete. The frozen
runtime passes the final local inventory below. The original PR's current
delivery section records the exact commit, same-commit CI outcome, artifact
identity and downloaded-package hashes; historical delivery entries below
must not be used as the evidence for this continuation.

### Implemented boundaries and review findings

- `CombatStop` separates an unadmitted inspection from actual motion
  ownership. The original route remains in control while future positions
  are being queried. A completed failed inspection cannot gain ownership
  merely because the normal driver changes yaw. A checked destination, a
  genuine newly opened same-point native lay, or another current legal point
  can create the next episode. The failure latch is not global to all targets.
- An admitted pivot retains its exact target and point through planning
  waits. Both the contact ID and the aim/face point are rebound before the
  ordinary live-target overlay, eliminating a second target's opposing turn.
  Physical progress, rotation refusal, task cancellation, target loss and
  current gun identity remain live boundaries. Missing geometry does not
  replay an old steering value, and continuing a pivot never grants fire.
- Current ordinary HE's qualified local contact work uses the existing
  foreground or same atomic slice before unrelated unknown penetration work.
  Historical damage hints are rechecked exactly. A high-damage hint whose
  current check is pending can yield to a current executable contact without
  converting the pending target into a zero-damage or armour-failed result.
  A newly proved current HE penetration still precedes an uncommitted fallback.
- Finite inspection progress is no longer keyed to the raw source position.
  Exact source poses still revoke all old positive and negative physical
  evidence. Future-position chord work freezes one explicit hypothetical
  source pose for the same destination, shell, target and point; it is never
  a current firing proof. Changed target/component/domain/lane observations
  restart it. Cancellation or replacement during the final native callback
  cannot publish the old plan or destroy a replacement task.
- Friendly obstruction uses the same selected-point task. The independent
  friendly side-choice, retry timer and arrival-success owner, its consumers,
  and the obsolete gun-angle adjustment/rejection store are deleted rather
  than left as fallbacks. Native ally collision and final shot-lane refusal
  remain. BOT death retires its shared control binding while preserving
  already committed launch records; object identity protects a replacement
  binding from an old close callback.
- The integration run caught and repaired a siege-mode admission regression
  introduced by narrowing ordinary recovery ownership. Clear native mode
  admission and explicit attack authority use the existing request/echo
  protocol. A cold wall or single-feature controller cannot acquire a new
  hull/mode permission. Existing siege and full-controller assertions are
  retained. Reload/switch intents are not reinterpreted as failed hydraulic
  geometry or a reason to discard an accepted movement task.

### Regression provenance and scope

New files cover policy scheduling, actual native future-ray work, shared
recovery liveness, BOT friendly recovery/lifecycle, and the reported opening
route plus loaded-HE execution chain. The latter uses the real shared policy,
driver, native evaluator adapter, trigger admission and ammunition accounting
with controlled native observations and deterministic query cost. Its HE
regression reached an actual committed shot and exactly one round deduction,
not merely an `aim` decision. This is still not a Windows #1513 playtest.

Pre-fix failures were retained for HE budget starvation, source-jitter review,
native lay loss during planning waits, unchecked cold recovery, pending
high-damage hints, future-ray progress, final-callback task cancellation,
target/sample mismatch and source-BOT death. A first draft of the live HE
fixture reused the source entity ID for an enemy; that fixture error was
corrected before the valid no-shot baseline was recorded and is not claimed
as a production defect.

Existing tests were migrated only where their expectations required retired
friendly APIs or admitted unchecked blockers/yaw-only retries. The new
expectations require unchanged actual route inputs until a checked goal.
Stationary-domain tests first establish a legitimate current-point combat
stop before testing a planning wait; they no longer depend on freezing an
already admitted pivot. Their negative-domain and no-fire assertions remain.
The original HE damage-ranking, penetration threshold, NEXT unknown-domain,
siege and controller tests are not weakened to hide failures.

The source diff leaves `ai/driver.py`, `ai/navigation.py`, `ai/traffic.py`,
`tank_collision.py` and `vehicle_control/route_tasks.py` unchanged. The only
`native_motion_core.py` change removes a write to the deleted friendly store.
No new test skip, query-budget increase, steering gain, collision bypass,
early current-HE unload, eight-second search or second recovery owner is added.

### Final local verification

Python 3.11.9 used the CI-pinned Pillow 12.3.0, NumPy 2.3.5, ModernGL 5.12.0
and glcontext 3.0.0 dependencies. The final complete run started after all
production and regression edits were frozen, and each test file ran in its own
interpreter to prevent native test doubles leaking between files.

| Gate | Observed result |
| --- | --- |
| Complete client inventory | 529/529 files passed; 10,721 reported tests, including 9 existing environment/resource skips |
| Complete launcher inventory | 49/49 files passed; 1,328 reported tests, with 170 recorded platform/display/resource skips |
| Shared-control ownership checker | 89 tests passed |
| Client source syntax under local Python 3.11 | All 262 modules compile; this is not the Python 2.7 package gate |
| 29-actor analytic shared-control workload | Completed; no-enemy case: 0 launches; mixed AP/HE case: 62 measured launches and 633 armour batches |
| Whitespace/integration diff | `git diff --check` passed; no remaining unstaged runtime edit |

The 29-actor workload recorded an unchanged runtime fingerprint before and
after execution across the 261 files in `offline_lan_0922`:
`afed59ce20df6639c5f44b34ce751ed1f0377443412df474fbc3840ec571db38`.
Its geometry is analytic and its timing is not a Windows-client FPS estimate.
Focused test totals overlap the full inventory and are not added to it.

The unchanged CI workflow must still compile and test with real Python 2.7,
rebuild the shipping x86 native module, compare every packaged client code
object with the same checkout, and build/run the extracted Windows launcher.
Delivery additionally compares the downloaded launcher's bundled Python
sources, build identity and nested client/wotmod bytes with that same run.
The exact post-build attestation belongs in the current PR delivery section,
so this handoff does not invent a future run ID or self-referential commit SHA.

### Native acceptance still required

Use the fresh artifact identified in the PR, not the rejected
`colorfulmeans-42796652971-1` package. The user's next playtest should check:

1. The same AT7 opening route with drive and fire enabled: no unchecked
   enemy inspection may alternate opposing chassis turns with navigation.
2. A target outside the actual gun arc: the original native hull actuator
   should continue the same accepted point through policy review waits.
3. Loaded ordinary HE: a legal current contact should reach an actual shot,
   while NEXT remains independent and does not unload the current cassette.
4. Current high-penetration ammunition: subsequent loading follows verified
   HE-penetration/AP/high-penetration order, not permanent loaded-shell bias.
5. World/friendly obstruction and arrival: retain the same point, revalidate
   at the actual destination, and return the original route on finite failure.
6. Capture/manual/return-base and target death: old movement/gun intentions
   must end without cancelling already committed projectile records.

No new exact Windows #1513 battle or subjective steering smoothness is claimed
by the local tests. Report the installed build identity with any remaining
opening-route, HE, recovery, turret-continuity or frame-pacing failure.

## Historical delivery record

## Authority and starting point

This continuation starts at the original open PR #119 head `d149aadc`, not
the older `D149AD` comparison as a new fork. The user's November 10 review
separates two previously conflated mechanisms:

- the eight-second search *after negative penetration review*; and
- the independent BOT `_gun_angle_order` which tried forward/reverse positions
  around eight **metres** away without proving the gun's selected aim point
  from those positions.

The old eight-second improvement search is removed, including its policy
action, eligibility, timestamps, movement proposals and shared-control special
cases. This is not a zero-second timer. Neither the existing native hull-turn
actuator nor the ordinary route/traffic/ground/collision laws are deleted.
The earlier `shared-he-recovery-contract-20261110.md` and November 9 handoffs
remain historical records; their claims that this eight-second search remains
active are superseded by this review.

## One aim-point owner and physical handoff

`AttackPolicy` chooses the current target, shell, mode and sample. When a
currently reviewed penetration/HE sample is physically blocked or outside
the installed gun's arc, `CombatStop` carries that **same** candidate into one
finite physical recovery episode. It does not ask another module to find a
generic nearby shooting position or reselect an aim point on arrival.

1. An actually executable stationary native hull/hydraulic lay takes priority
   over translation. Stationary review and its pending observations do not
   manufacture a new destination.
2. A genuinely blocked same-point candidate can request projected positions.
   Each position must pass normal navigation checks and the native evaluator's
   future line of sight for the **same shell, target and sample**. Partial
   native queries remain pending; a destination preview never grants fire.
3. The ordinary physical driver executes only the checked destination. The
   phase survives unrelated new candidates and macro target hints. The gun
   target and drive target are both rebound to the phase's original target.
4. Reaching the destination only requests current-pose revalidation. The
   original actual barrel, lane, armour/HE and trigger-admission checks remain
   separate. A recent planned solution cannot stand in for a launch proof.
5. Finite destination exhaustion or a six-second lack of physical progress
   retires the combat movement lease, clears its stopping/turning instructions
   and returns the authored task order. The same failed pose cannot acquire
   the identical task every callback; material source/target motion or fresh
   executable native evidence can open a new episode.

`bot_runtime._gun_angle_order` and its obsolete combat-order call are removed.
The original rear-laying contact and movement safety mechanisms are retained
where they still have independent physical uses. The common combat lease
prevents a separate rear pursuit from co-owning movement.

Capture/parking/explicit travel keep their original translation authority.
An already-occupied capture position may turn a limited gun in place only
after a valid native primary-target laying proposal. A wall-blocked capture
hint cannot steal that hull turn. Mission cancellation clears retained gun
intentions before the next cached physical slice.

## Ammunition and trigger ownership

- With a complete negative penetration review, an available HE fallback is
  considered **immediately**, without an eight-second motion search. A
  verified penetrating shell still fires normally; unknown geometry never
  certifies negative armour.
- Ordinary HE applies its one-point-per-enemy penetration trial to fallback
  contact comparison as well. Only whitelisted high-penetration HE/HESH retains
  full weak-point validation.
- The physically loaded HE round/clip can execute a verified legal current
  contact even when a different enemy remains under review. Independently
  completed `NEXT` evidence selects only the subsequent load; it cannot
  unload or preempt an already admitted current HE trigger.
- HE contact failure may terminate the engagement only after actual complete
  native no-contact evidence; world/friendly blocks and unknown geometry are
  not fabricated no-contact certificates. Actual zero-damage contact remains
  a legal result.
- Retained gun intention only preserves *which point to re-aim at*. Every
  physical first trigger still needs a fresh actual-pose, actual-lane and
  ammunition proof. Dead/despawned targets cannot remain in cached aim input.
- The first-trigger native `auto_world_blocked` receipt now identifies whether
  the hit was on the actual **centre** barrel path or the **scattered** path.
  A centre-path or confirmed wreck obstruction invalidates that point's
  present lane and may request recovery. One scattered ray striking nearby
  geometry refuses that particular trigger with no debit, but does not turn
  an otherwise clear centre point into an automatic movement task. Its next
  trigger still repeats the entire native admission; no shot proof is cached.

## Verification boundaries

Host CPython tests exercise the real shared source with native-observation
fixtures, not Windows BigWorld itself. The frozen local source passed:

- Complete client test inventory: **524/524 files**, **10,666** executed
  methods (**10,657 passed; 9 skipped; 0 failures**).
- Complete launcher inventory: **49/49 files**, **1,328** executed methods
  (**1,158 passed; 170 host/platform skips; 0 failures**).
- The earlier separate `test_player_*.py` pass: **882/882** tests (before
  the additional scatter-refusal regression was added).
- `test_shared_*.py`: **277/277** tests.
- `tools/check_shared_vehicle_control.py --check`: **89/89** tests.
- Capture/contact handoff: **11/11** tests; complete navigation receipts:
  **22/22** tests.
- The 29-actor real worker-scheduling analytic workload committed **101**
  measured launches with exactly matched ammunition debits and no background
  work-quota violations. Its mixed-control CPU mean was **119.320 ms** per
  analytic 100 ms callback on this host; this is not game FPS or a guaranteed
  performance gain. The benchmark now reports the actual point recovery and
  HE fallback state instead of reading the deleted search timer.

The first full client run produced two *environment* errors: the partial
Git clone lacked historical `19d79b1` map blobs referenced by the unchanged
Great Wall and tactical-route tests. Fetching all 42 map blobs restored their
actual historical fixtures. Direct reruns passed **2/2** and **20/20** tests,
respectively. The subsequent full **524/524** source-tree run passed with no
changes to those tests or the routes. The first errors are preserved in the
local logs; they are not reported as a production navigation defect or hidden
from the verification history.

### First GitHub CI caught a real HE scheduling fault

Run [42786557537](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/42786557537)
on head `e222f7b3` completed navigation, native geometry, Windows server/editor
and BOT regression jobs successfully, but its 524-file client job found three
failures in `test_shared_current_he_execution.py` (one failed test file;
the other 523 passed). Its Windows launcher job was consequently skipped;
**no Windows launcher artifact from that run is a valid delivery.**

The CI runner's slower 8 ms native observation slice finished the lower-damage
HE target 14 while the also-negative-armour target 2's higher-damage contact
still had a real `atomic_frame_budget_exhausted` receipt. The policy published
an irrevocable CURRENT aim lock on target 14 before the second comparator
could obtain its fair callback. The outcome is reproducible locally with a
virtual atomic clock that consumes precisely the original wall-clock budget.
This is a genuine first-trigger ranking defect, not a missing fixture, CI
network error, or reason to weaken the three existing expectations.

The follow-up fix postpones **only that first lock** while a currently
penetration-qualified competitor has an explicitly native-budget-exhausted
HE comparison. Its unfinished query must receive an ordinary future slice;
there is no replacement movement timer, extra quota or assumed damage.
A competitor that truly returns `pending`, disappears, changes pose or lacks
positive penetration-failure qualification must not hold an independently
executable loaded HE hostage. Existing tests asserting those distinctions
remain unchanged and pass. New
`test_expensive_second_he_contact_cannot_lock_a_lower_damage_first_target`
forces the budget-expiration schedule without sleeping or stubbing the actual
evaluator. The 23-file shared-control test inventory passed after this fix;
the exact CI Python 3.11.9 dependency set then passed the **entire 524/524**
client file inventory: **10,667** methods, **10,658 passed, 9 skipped, 0
failures**. The standalone 89/89 shared-owner checker also passed. Two fresh
29-BOT worker10 native analytic schedules passed their original quota and
ammunition constraints with respectively **100** and **101** launches and no
background quota overruns; those variable wall-limited counts are not FPS.
The fresh Windows Python 2.7 build and exact downloaded launcher remain
separate CI gates.

### Follow-up CI package and same-run download correction

The corrected head `c75908f4` passed the complete
[Tests run 42792625606](https://github.com/colorfulmeans/wot-0.9.22-offline-battles/actions/runs/42792625606)
client job: 524/524 files, 10,667 methods with 9 skips, plus 49/49 launcher
files, 1,328 methods with 170 platform skips. Navigation, native geometry,
Windows server/editor and the Windows first-chance exception probe passed.
The actual Python 2.7 bytecode and native x86 source stamp were built and
checked in that run. The separately scheduled BOT regression job **failed one
of the 15 cases** in `test_shared_current_he_execution.py`: the expensive
second HE contact was skipped entirely when the atomic frame budget elapsed
immediately after evaluating the first contact. A lower-damage first target
could thus be prematurely locked. Both an explicitly budget-exhausted second
row and a wholly unvisited qualified second contact now defer the first lock
until their expected-damage results can be compared. Dedicated virtual-clock
regressions cover both shapes without increasing the per-frame budget or
relaxing the existing highest-damage HE assertion. The follow-up CI run, not
this failed run, must demonstrate BOT success.

Its Windows launcher was built and **uploaded successfully** as artifact
`13752143372`, 68,578,817 bytes, SHA-256
`d0463d89141ba954c9628a292b34af2d26f537d158906c2b9726439281737fa1`.
An independent download of those exact bytes passed outer ZIP CRC, the x64
launcher PE identity, all **265** bundled server/shared-control Python source
comparisons, the nested client ZIP and `.wotmod` CRCs, shipping x86 native
source stamp, starter equality and replay reader identity. This validates
contents, not execution of the Windows GUI on Linux.

The final Windows job nevertheless failed **after upload**: an immediate
`actions/download-artifact@v4` REST artifact-ID lookup returned `Not Found`
for its freshly uploaded ID. Consequently its downloaded-executable server
smoke step did not run, and that CI run is not reported as all green. The
follow-up workflow uses the documented same-run artifact **name** download
without cross-run `github-token`/REST-ID lookup, retaining the exact
one-extraction Windows server-startup assertion. No shipping gameplay source
or client tests were relaxed for this workflow repair; a new CI result must
pass before the package is considered fully delivered.

The GitHub Actions BOT group, full client suite, actual Python 2.7 compiler,
Windows launcher packaging and user in-game regression remain separate final
gates. Neither a host pass nor a future-path probe proves an actual game shot,
frame-time improvement, or fixed live AT7/STB1 presentation. The final PR
record must cite a specific new pushed SHA, completed CI run and downloaded
Windows artifact; the prior `d149aadc` package is **not** this correction.
