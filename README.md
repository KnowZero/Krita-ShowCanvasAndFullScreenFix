# Krita-ShowCanvasAndFullScreenFix
This is a temporary plugin that overrides the shortcuts for show canvas, full screen and toggle dockers to maintain canvas position.(Krita 5)



<h2>Show-Canvas And Full-Screen Fix</h2>
<h4>v.0.01</h4>
This is a temporary plugin that overrides the shortcuts for show canvas, full screen and toggle dockers to maintain canvas position.(Krita 5)

<h2>Usage Details</h2>

<p>Go to Tools->Show-Canvas And Full-Screen Fix->Enable to activate.</p>

<p>After activation, you can use show canvas(TAB), full screen(CTRL+SHIFT+F) and toggle dockers(configure in shortcut manager) to use. The plugin is shortcut aware so if you change to custom shortcuts, it will still work just fine. Using show canvas, full screen or toggle dockers from the Menu will use the OLD functionality. This has been left untouched so one can test both side by side.</p>

<p>This script will by default create a temporary overlay to reduce flickering. You can increase/lower it in Tools->Show-Canvas And Full-Screen Fix->Config... (0 would disable the overlay)</p>

<h2>Important</h2>

<p>Please report any issues with wrong positioning, flickering or other issues on krita-artists at https://krita-artists.org/t/show-canvas-and-full-screen-position-fix-plugin-krita-5/33515 (Make sure to include your operating system and if you are using subwindow or tab document mode. Videos of issues are welcome). If you do not experience flickering with the default 200ms setting, try lowering it or setting it to 0 and please report your experience.</p>

<p>This plugin exists to help test a patch that will try to make it into Krita 5.1, so please report both positive and negative results. If you are using Krita 5.1 Alpha, do pay attention when this patch does hit master so that you can disable this plugin to avoid issues.</p>

