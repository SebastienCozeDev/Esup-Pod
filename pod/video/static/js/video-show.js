var translationDone = false;

document.getElementById('podvideoplayer_html5_api').addEventListener('play', function () {
    if (!translationDone) {
        const elementToTranslateList = [
            ['.skip-back', gettext('Seek back 10 seconds')],
            ['.skip-forward', gettext('Seek forward 10 seconds')],
            ['.vjs-quality-selector', gettext('Quality')],
            ['.vjs-mute-control', ''],
        ]
        for (let elementToTranslate of elementToTranslateList) {
            translateTitleOfVideoPlayerButton(elementToTranslate[0], elementToTranslate[1]);
        }
    }
});


/**
 * Translate the title of the video player button.
 *
 * @param {string} querySelectorButton The query selector for the button.
 * @param {string} title The title.
 */
function translateTitleOfVideoPlayerButton(querySelectorButton, title) {
    let translatedTitle = title;
    const videoPlayerButton = document.querySelector(querySelectorButton);
    if (videoPlayerButton) {
        const videoPlayerSpan = videoPlayerButton.querySelector('.vjs-control-text');
        videoPlayerButton.title = translatedTitle;
        if (videoPlayerSpan) {
            videoPlayerSpan.textContent = translatedTitle;
        }
    }
}
