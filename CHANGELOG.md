# Changelog

The most recent section is used by `scripts/build_exe.py --release` as the
release notes: first the introduction, then the list of changes.

## 1.0.2

A new **Images** page for figures made from photographs, numbered points with notes and a button that inserts the figure with its caption into Word, more arrow options, and the user manual readable inside the program.

- **Images page**: one to four photos on a sheet (eleven layouts, five formats), loaded from files, dropped or pasted; wheel and drag frame each photo in its cell. The same annotations as the video, plus **Link**: two rectangles or ovals joined by a line. Annotations belong to the photo they lie on and follow it when it is panned or zoomed; an arrow or a link between two photos has one end on each, and an annotation straddling two photos stays whole. Export to PNG or JPG, copy to the clipboard.
- **Numbered points** (Numbers / Letters): a circle with a number or a capital letter, always the next after the last one, one point per press of the button; in the video they follow a subject like the other figures.
- **Caption and Word**: in the Images page every point has a note; the Caption button holds the text after "Figure N :"; the **Word** button inserts picture and caption into the open Word document at the cursor, in the Caption style with the automatic SEQ number (cross-references and table of figures work), with an RTF clipboard fallback.
- **Images project**: saved as an editable JSON with a `<name>_file` folder of copies of the photos and images; Open / Save / Save as, undo and redo for everything.
- **Arrows**: heads at the tip, the tail, both or none, in five styles; in the video the **Tail** can stay fixed where it was drawn while the tip follows the subject.
- **Timeline**: every effect on its own row in the order it was added; *Extend to cursor* keeps tracking and, if the subject is lost, leaves the figure where it was last seen.
- **Manual**: a *Manual* entry in the bar on the left opens the user manual in a window with table of contents and language menu, in the language of the interface; the manual is bundled in the executable. Manuals in the nine languages rewritten for the new features, with a chapter on the Images page and all screenshots retaken.

## 1.0.1

Fixes from a code review of 1.0.0 (thanks to SOsintOps for the detailed reports, issues #1–#12) and an export error with added audio tracks. Updating is recommended.

- **Export with an added audio track** no longer fails with "Media type mismatch" (a label clash in the ffmpeg filter graph introduced in 1.0.0).
- **Audio after a cross-fade**: the exported audio is no longer shorter than the video by half the fade at every cross-fade (#1).
- **Tracking** falls back to template matching when OpenCV has no VitTrack support, instead of failing (#2).
- **Safer saving**: project and settings are written atomically, so a failed save never leaves a truncated file (#4); an export always works on a copy of the project, so editing during an export cannot affect it (#6), and a failed export no longer leaves a partial MP4.
- **Responsiveness**: reading the information of an imported video or audio file happens in the background, with a cancellable progress window, and ffmpeg calls have timeouts (#8).
- **ffmpeg download** is checked against the SHA-256 fingerprint published by gyan.dev before it is installed; the VitTrack model is downloaded from a fixed commit of opencv_zoo matching its fingerprint (#11).
- **Robustness**: errors in background callbacks no longer stop the interface updates (#3), a possible deadlock when closing video sources is removed (#5), preview audio uses one temporary file per job and deletes it (#9), timeline thumbnails release their video files (#10), and several minor fixes (#12).
- **Requirements**: Pillow 10.1 and OpenCV 4.9 or later; the program checks at start that Python is 3.11 or later (#7).

## 1.0.0

First release of EditSimple, a simple video editor made to explain a fact or show evidence in a video: import the footage, point at what matters, and arrows, boxes, zooms and pixelations follow the subject on their own; where the tracking goes wrong, drag the figure back onto the subject. In a few minutes you get an MP4 ready to show, with opening and closing slides, texts, logo and the operator's signature.

- **Subject tracking**: boxes, ovals, arrows, zooms and pixelations follow a person, a face, an object or a vehicle, grow and shrink with it when it comes closer or moves away, and end on their own when it leaves the frame (they follow it out until it is completely gone, so no frame is left uncovered). The optional VitTrack model (downloaded on request) helps find the subject again behind an obstacle.
- **Keyframes**: where the tracking is wrong, drag the figure onto the subject in the preview; the path is corrected before that point and tracking restarts from there to the next keyframe. Keyframes and tracking points can be selected and deleted on the timeline.
- **Arrow on a subject**: the arrow follows a rectangle drawn around the subject, keeping its tip on it.
- **Zoom** from 2x to 16x, rectangular or oval, in a box placed anywhere, with an outline and a line linking it to the object.
- **Pixelation**, rectangular or oval, for faces and plates.
- **Texts** on several lines (alignment, font, size, colour, shadow, background with opacity and rounded corners), **images** over the video, **logo and operator text** fixed in a corner, **elapsed time** and **frame number** written in the video.
- **Slides** at the start, at the end or in the middle, with a solid colour or a background image; texts and images go on top.
- **Speed** from 0.25x (slow motion) to 32x (fast forward), with an optional clock icon showing the speed.
- **Cut, delete, freeze frame**, clips reordered by dragging; **transitions**: from black, to black, cross-fade with the next clip.
- **Audio**: added tracks (commentary, music) with volume and fade in/out, original audio with volume, fades and removal of single stretches, a white line showing the volume on every track; preview playback with sound.
- **Timeline**: film strip down to single frames, effect lanes that scroll vertically, an eye to hide or show an effect, right-click menu to extend an effect to the cursor or stop it there, resizable split between preview and timeline.
- **Preview**: zoom with Ctrl+wheel and pan, playback backwards, ±10 frames, and a button to **detach** it into a separate window (and dock it back).
- **Export** to MP4 (H.264 + AAC) identical to the preview.
- **Interface in 9 languages** (English, Italian, German, French, Spanish, Dutch, Polish, Greek, Albanian), switched without restarting, and a **user manual** with screenshots in every language in `docs/manual`.
- ffmpeg and the VitTrack model are not included: the Configure page downloads them into the `tools` folder next to the program, with their licenses.
