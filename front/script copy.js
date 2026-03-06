document.addEventListener("DOMContentLoaded", () => {
    const mainMenu = document.getElementById("main-menu");
    const urlInputSection = document.getElementById("url-input-section");
    const downloadStatusSection = document.getElementById("download-status");
    const downloadStatusText = document.getElementById("download-status-text");
    const spinner = document.querySelector(".spinner");
    const videoUrlInput = document.getElementById("video-url");
    const pasteButton = document.getElementById("paste-url");
    const downloadButton = document.getElementById("download-btn");
    const backButton = document.getElementById("back-btn");
    let downloadType = "";

    function showUrlInput(type) {
        downloadType = type;
        mainMenu.style.display = "none";
        urlInputSection.style.display = "block";
        downloadButton.style.display = "none"; // Ocultar botón hasta que haya URL
        pasteButton.style.display = "inline-block"; // Asegurar que el botón de pegar esté visible
    }

    function backToMenu() {
        mainMenu.style.display = "block";
        urlInputSection.style.display = "none";
        downloadStatusSection.style.display = "none";
        videoUrlInput.value = ""; // Limpiar el input
        pasteButton.style.display = "inline-block"; // Restaurar el botón de pegar
        downloadButton.style.display = "none"; // Asegurar que el botón de descargar esté oculto
    }

    function updateDownloadButton() {
        if (videoUrlInput.value.trim()) {
            pasteButton.style.display = "none";
            downloadButton.style.display = "inline-block";
        } else {
            pasteButton.style.display = "inline-block";
            downloadButton.style.display = "none";
        }
    }

    function pasteUrl() {
        navigator.clipboard.readText().then(text => {
            videoUrlInput.value = text;
            updateDownloadButton();
        }).catch(err => console.error("Error al leer el portapapeles", err));
    }

    async function startDownload() {
        if (!videoUrlInput.value.trim()) return;

        urlInputSection.style.display = "none";
        downloadStatusSection.style.display = "block";
        downloadStatusText.textContent = "Descargando...";
        spinner.style.display = "block"; // Asegurar que el spinner aparezca

        const request = `${downloadType}***${videoUrlInput.value.trim()}`;

        try {
            if (downloadType.includes("playlist")) {
                for (let i = 1; i <= 3; i++) {
                    downloadStatusText.textContent = `Descargando ${i}/3...`;
                    await pywebview.api.simulate(request);
                }
            } else {
                await pywebview.api.simulate(request);
            }
        } catch (error) {
            console.error("Error en la descarga", error);
        }

        downloadStatusText.textContent = "Descarga completada!";
        spinner.style.display = "none"; // Ocultar el spinner

        // Volver al menú principal después de 3 segundos
        setTimeout(backToMenu, 3000);
    }

    // Eventos
    document.getElementById("mp3-btn").addEventListener("click", () => showUrlInput("mp3"));
    document.getElementById("playlist-mp3-btn").addEventListener("click", () => showUrlInput("playlist_mp3"));
    document.getElementById("mp4-btn").addEventListener("click", () => showUrlInput("mp4"));
    document.getElementById("playlist-mp4-btn").addEventListener("click", () => showUrlInput("playlist_mp4"));
    pasteButton.addEventListener("click", pasteUrl);
    downloadButton.addEventListener("click", startDownload);
    backButton.addEventListener("click", backToMenu);
    videoUrlInput.addEventListener("input", updateDownloadButton);
});
