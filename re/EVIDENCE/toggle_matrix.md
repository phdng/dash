# EVIDENCE/toggle_matrix.md — P3-1 /var/tmp knobs (session-005)
_P اسپ: grep `"/var/tmp/duodash_[a-z_0-9]+"` toàn decompile/ = 302 hits `duodash_`, ~150 literal paths bên dưới._
_Semantics: **KILL** = file tồn tại → disable feature; **VALUE** = đọc nội dung; **ONESHOT** = tạo → consume + unlink._
_Tồn tại = CONFIRMED (grep line). Semantics = CONFIRMED nếu đã đọc body (sessions trước), ngược lại HYPOTHESIS-theo-tên._

## Quy ước đã xác minh (mẫu)
- `access(path,0)==0` (tồn tại) → skip/disable; `stat()!=0` (vắng) → cho phép (F-025 §8-9).
- `fileExistsAtPath:` YES → disable (1E770:20, 1C3C8:15...). Ngoại lệ đảo: `kp_auxnoswap` (byte=!exists, 3E428:20).

## A. Kill-switches KILL (exists = disable) — CONFIRMED pattern
| Knob | Site | Effect (CONFIRMED nếu đã đọc body) |
|---|---|---|
| duodash_ab_hosting_off | 1C3C8:15 | MASTER: mọi intercept dock/focus/home/icon skip |
| duodash_ab_noroster | 1E770:20 | Roster OFF (byte_162E28=0) |
| duodash_ab_nohomedismiss | 1C29C:25 | Giữ home, không teardown |
| duodash_ab_noswitchteardown | 1CCF4:25 | Không teardown app khác khi dock/icon-tap (đk >0.5s) |
| duodash_ab_aggressive_focusteardown | 1BF1C:111 | Mở rộng teardown cả TemplateUIHost (ngược: không file → tha TemplateUIHost) |
| duodash_ab_nodiscoclose | 7B9EC:25, 7BC14:26 | Không arm + không fire disconnect-kill |
| duodash_ab_noreap | 763E0:92, 7792C:128 | Không SIGKILL (cả 2 paths) |
| duodash_ab_nokeypane | 38240:85 | Từ chối dựng card (unified KB off ở SB) |
| duodash_ab_nokprecover | 37A7C:48 | Không rebuild khi keyboard lost |
| duodash_ab_noautostart | 1A820:18 | Không autostart launch |
| duodash_ab_nodashlaunch | 19330:90 | Không launch dash (nhánh navprovider) |
| duodash_ab_nodashkeep | 116D4:21 | Bypass autostart-keep (116D4 trả sớm) |
| duodash_ab_nocpui | 626B4:25, 22E40:152 | Không CPUI (2 sites) |
| duodash_ab_nopaneactivity | 17204:35 | Suppress post paneactivity (byte_1637F0=1) |
| duodash_ab_nonavhide | 792C4:19 | Không nav-hide (đk byte_1646B0==0) |
| duodash_ab_nomediahide | 79434:792 | Không media-hide |
| duodash_ab_navhide_respring | 7B1A8:17 | Respring sau nav-hide (đảo: CÓ file mới respring, a1+32==1) |
| duodash_ab_noconfigrepair | 27E20:542 | Skip config-repair (result=skipped why=knob) |
| duodash_ab_nosplash | 358F0:63 | Không splash |
| duodash_ab_nonotice | 345E4:56 | Không notice |
| duodash_ab_noswap / nogutterctrl | 54558:164,166; 55EDC:31; 56E7C:31,33; 62BBC:16; 62C40:22 | Không swap panes / gutter control |
| duodash_ab_noresize / resize_nopulse / resize_nodrag | 5FD10:28; 60AAC:37; 60F6C:388 | Không resize/pulse/drag |
| duodash_ab_nopicker + picker_nopulse/nosnap/noblur/nodrop/nowake/nospin/panesized/handle/nohandle/noswiperecover | 304DC:43,44,50; 3257C:386,394,400,406; 70270:15; 57B28:18; 57C60:299,862; 5A004:38; 525D8:147; 4E358:33; 4E584:25; 5752C:38; 5794C:80; 5FD10?; 4F6E8:56; 51594:63 | Picker UX kill-switches (HYPOTHESIS chi tiết từng cái) |
| duodash_ab_nomaximize / nomaximize_cpui | 5401C:63,69; 2E874:196,208 | Không maximize |
| duodash_ab_nomat ×2 | 2D8A0:51; 3257C:226 | Không mat render |
| duodash_ab_norehostinplace | 2DE28:175 | Không rehost in-place |
| duodash_ab_nolivepresent / livepresent_nogroup/commit/noop | 2A610:106,131,185,189 | Live-present kills (HYPOTHESIS) |
| duodash_ab_nonudge / nonudgetick | 2A3E0:21; 370F8:21 | Không nudge tick |
| duodash_ab_nobubble / nobubblesettings / bubble_noblink/nobeep/nodrag/noavaudio/nofake | 74A98:47; 62194:21; 74924:40,46; 74A98:102; 755A0:50; 76154:17; 71100:46 | Navbubble kills (HYPOTHESIS) |
| duodash_ab_nogps | 71BC0:23 | Không GPS |
| duodash_ab_nolayoutui / nolayoutconfirm | 67C38:58,205 | Không layout UI/confirm |
| duodash_ab_nohitopaque | 6E824:33 | Không hit-opaque |
| duodash_ab_noevict / evict_skipfrontmost | 3AE50:61,66; 3B2D8:159,166 | Không evict / skip frontmost khi evict |
| duodash_ab_split_evict | 3CC44:309 | Split-evict gate |
| duodash_ab_nokporient | 39D4C:88 | Không KP orient |
| duodash_ab_noscenegeom | 3E9A8:21 | Không scene geometry override |
| duodash_ab_nopresupdate | 40AE8:27 | Không present-update |
| duodash_ab_toapps_swallow | 41730:95 | Swallow to-apps transition |
| duodash_ab_nopaneorient | 41C24:20 | Không pane orient |
| duodash_ab_noidlehold | 4D6B0:47 | Không idle-hold (đk stat!=0 mới hold) |
| duodash_ab_keepawake_off | 4D158:35, 4DEB4:23 | Không hook blank (MSHook chỉ khi VẮNG); 4D158 keepawake gate |
| duodash_ab_norespring (duodash_ prefix) | 8097C:28 | Không respring (stat!=0 mới làm) |
| duodash_no_msrv_restart | 81344:56 | Không restart mediaserverd |
| duodash_siriprobe_off | 889D0/88BC8/88C98/88D7C/88E2C/88EA0/88F48:16, 89764:17, 89880:16 | SiriProbe hook bypass (via 894F0 gate) |
| duodash_siriprobe_swallow (+_id) | 89764:21,27 | Swallow Siri request (P3-4 còn lại: swallow vs log chi tiết) |
| duodash_no_rpcgate | 971FC:44 | Không RPC gate (access!=0 → gate?) |
| duodash_kp_noauxsid / kp_noapplydiff | 3C368:95,101 | Keypane aux/session/adiff kills |
| duodash_kp_auxnoswap | 3E428:20 | ĐẢO: byte = !exists |
| duodash_ab_kbwidth_off ×2 | 46340:332, 49B44:35 | Không KB width override |
| duodash_cpui_nowithdraw | 10188:28 | Không withdraw CPUI (đk access!=0 mới withdraw) |
| duodash_cpui_norefg | 11CAC:198 | Không refg (delta>=0.5) |
| duodash_cpui_norebind | 11CAC:288 | Không rebind (delta<1.0 hoặc tồn tại) |
| duodash_cpui_nonudge ×2 | 127F0:30, 12D84:49 | Không nudge (access!=0 mới nudge) |
| duodash_cpui_noelemguard | 18F48:19 | Bỏ hook FBSDisplayLayoutPublisher addElement |
| duodash_cpui_nogeomhook ×6 | 1B23C:23, 1B38C:31, 1B4AC:23, 1B5DC:31, 1B6FC:21, 1B804:29 | Không geometry override (access!=0 mới apply) |
| duodash_cpui_nodeathwait | C2A4:25 | Không death-wait |
| duodash_cpui_noeventlaunch | C37C:79 | Không event-launch |
| duodash_cpui_nodockhide | B144:96 | Không dock-hide (!access \|\| ...) |
| duodash_cpui_noexitdismiss | 1F954:33 | Không exit-dismiss (length && access!=0) |

## B. VALUE files (đọc nội dung) — CONFIRMED sites
| File | Site | Đọc thế nào |
|---|---|---|
| duodash_ab_clearpanes (+.done) | 74C8:105-200 | mtime vs done+0.5 → xóa 8 keys; one-shot remove |
| duodash_ab_fontfloor_force | 7EA4:28-57 | trim + digits + clamp 97 |
| duodash_ab_discoclose_secs | 7B9EC:34-50 | double [0,120]s, else 12s |
| duodash_ab_holdsec | 163EC:350,456 | double clamp [10,3600] else 900s |
| duodash_ab_host / hostsplit / splitstart / spike | 163EC:324,380,491,310 | non-empty trim → one-shot actions + removeItem |
| duodash_ab_reapdelay | 202D0:202-224 | double clamp (0,60] else 0.0 |
| duodash_ab_panepad / layout / panefracs / paneratio / content_inset / mat_alpha / rscale / canvas / orient / lscape / rotate / gps_bundle / simspeed / splash_secs / dashsettle / dashlaunch_secs / bubble_* / livepresent_alpha/target/anim / keypane_hidegap / lang_force / forceio / forcepush / forcerelayout | 218D8:399-506; 29BC4:79; 33DB4:19; 3B2D8:89,107; 3DFC8:19; 3CC44:128; 2BF84:103; 706A0:31; 71780:165; 358F0:201; 1A18C:19; 19A08:25; 38E14:22; 9AFB0:38; 42124:20; 34C44:19; 42498:108; 2A610:116,136,241 | Giá trị số/chuỗi override (HYPOTHESIS chi tiết từng cái) |
| duodash_ab_display_held | 4DEB4:16, 4D4F8:23, 4D5E4:15 | ONESHOT: tồn tại + backlight<0.2 → SetScreenBlanked(1) + unlink; open(513) tạo |
| duodash_norespring / respring_soft | 8097C:28; 9DB88:24 | stat-gated respring path |
| duodash_cr_off / cr_dryrun | 9E014:104,229 | access-gated crash upload/local-only |
| duodash_kbpoc_kbd | 4C858:25 | Gate kbd PoC hooks (exists = ENABLE — ngược KILL) |
| duodash_ab_cptrip (/tmp/) | 455D0 cptrip branch (session-002) | Gate NSBundle localizedString hook |

## C. Thống kê
- ~100 literal knobs riêng biệt (302 hits gồm lặp). KILL ~80, VALUE ~25, ONESHOT ~10.
- Đảo semantics: kp_auxnoswap (byte=!exists), kbpoc_kbd (exists=enable), navhide_respring (exists=do), iconadd (exists=do branch).
- Chưa đọc body (UNKNOWN effect chi tiết, HYPOTHESIS-theo-tên): toàn bộ picker/*, livepresent/*, bubble/*, layout/pad/fracs/ratio, mat/rscale/canvas, gps/simspeed, keypane_hidegap, orient/lscape/rotate, force*.
