document.addEventListener("DOMContentLoaded", () => {
    const mainMenu = document.getElementById("main-menu");
    const urlInputSection = document.getElementById("url-input-section");
    const downloadStatusSection = document.getElementById("download-status");
    const downloadStatusText = document.getElementById("download-status-text");
    const spinner = document.querySelector(".spinner");
    const videoUrlInput = document.getElementById("video-url");
    const pasteButton = document.getElementById("paste-url");
    const downloadButton = document.getElementById("download-btn");
    const loadPlaylistButton = document.getElementById("load-playlist");
    const selectAllButton = document.getElementById("select-all");
    const deselectAllButton = document.getElementById("deselect-all");
    const downloadSelectedButton = document.getElementById("download-selected");
    const cancelDownloadButton = document.getElementById("cancel-download");
    const backButton = document.getElementById("back-btn");
    const playlistDirInput = document.getElementById("playlist-dir");
    const playlistSection = document.getElementById("playlist-section");
    const playlistTitleEl = document.getElementById("playlist-title");
    const playlistItemsEl = document.getElementById("playlist-items");
    const downloadStatusTitle = document.getElementById("download-status-title");
    const urlInputs = urlInputSection.querySelectorAll("input");
    let downloadType = "";
    let playlistTitle = "";
    let statusTimer = null;

    function showUrlInput(type) {
        downloadType = type;
        mainMenu.style.display = "none";
        urlInputSection.style.display = "block";
        downloadStatusSection.style.display = "none";
        downloadButton.style.display = "none";
        downloadSelectedButton.style.display = "none";
        cancelDownloadButton.style.display = "none";
        loadPlaylistButton.style.display = type.includes("playlist") ? "inline-block" : "none";
        selectAllButton.style.display = "none";
        deselectAllButton.style.display = "none";
        pasteButton.style.display = "inline-block";
        if (type.includes("playlist")) {
            playlistDirInput.style.display = "block";
        } else {
            playlistDirInput.style.display = "none";
            playlistDirInput.value = "";
        }
        urlInputs.forEach(input => {
            input.style.display = input.id === "playlist-dir" ? playlistDirInput.style.display : "block";
        });
        playlistSection.style.display = "none";
        playlistTitleEl.textContent = "";
        playlistItemsEl.innerHTML = "";
    }

    function backToMenu() {
        mainMenu.style.display = "block";
        urlInputSection.style.display = "none";
        downloadStatusSection.style.display = "none";
        videoUrlInput.value = "";
        playlistDirInput.value = "";
        playlistDirInput.style.display = "none";
        urlInputs.forEach(input => {
            input.style.display = "block";
        });
        pasteButton.style.display = "inline-block";
        downloadButton.style.display = "none";
        downloadSelectedButton.style.display = "none";
        cancelDownloadButton.style.display = "none";
        loadPlaylistButton.style.display = "none";
        selectAllButton.style.display = "none";
        deselectAllButton.style.display = "none";
        playlistSection.style.display = "none";
        playlistTitleEl.textContent = "";
        playlistItemsEl.innerHTML = "";
        playlistTitle = "";
        stopStatusPolling();
    }

    function updateDownloadButton() {
        if (videoUrlInput.value.trim()) {
            pasteButton.style.display = "none";
            if (downloadType.includes("playlist")) {
                loadPlaylistButton.style.display = "inline-block";
                downloadButton.style.display = "none";
            } else {
                downloadButton.style.display = "inline-block";
            }
        } else {
            pasteButton.style.display = "inline-block";
            downloadButton.style.display = "none";
            loadPlaylistButton.style.display = "none";
            selectAllButton.style.display = "none";
            deselectAllButton.style.display = "none";
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
        mainMenu.style.display = "none";
        downloadStatusSection.style.display = "block";
        downloadStatusTitle.style.display = "block";
        downloadStatusText.textContent = "Iniciando...";
        spinner.style.display = "block";

        try {
            const result = await pywebview.api.download_single({
                format: downloadType,
                url: videoUrlInput.value.trim(),
            });
            if (typeof result === "string" && result.toLowerCase().includes("error")) {
                downloadStatusText.textContent = result;
                spinner.style.display = "none";
            } else {
                startStatusPolling();
            }
        } catch (error) {
            console.error("Error en la descarga", error);
            downloadStatusText.textContent = "Error en la descarga";
            spinner.style.display = "none";
        }
    }

    async function loadPlaylist() {
        if (!videoUrlInput.value.trim()) return;

        urlInputSection.style.display = "none";
        downloadStatusTitle.style.display = "none";
        downloadStatusText.textContent = "Leyendo playlist...";
        downloadStatusSection.style.display = "block";
        spinner.style.display = "block";

        try {
            const result = await pywebview.api.get_playlist_items(videoUrlInput.value.trim());
            if (result.error) {
                downloadStatusText.textContent = result.error;
                spinner.style.display = "none";
                urlInputSection.style.display = "block";
                return;
            }
            playlistTitle = result.title || "";
            playlistTitleEl.textContent = playlistTitle ? `Playlist: ${playlistTitle}` : "Playlist";
            playlistItemsEl.innerHTML = "";
            const table = document.createElement("table");
            table.className = "playlist-table";
            const tbody = document.createElement("tbody");

            result.items.forEach((item, idx) => {
                const row = document.createElement("tr");
                const checkCell = document.createElement("td");
                const textCell = document.createElement("td");
                const checkbox = document.createElement("input");

                checkbox.type = "checkbox";
                checkbox.checked = false;
                checkbox.dataset.url = item.url || "";
                checkbox.dataset.title = item.title || `Video ${idx + 1}`;

                checkCell.className = "playlist-check";
                textCell.className = "playlist-title";
                textCell.textContent = checkbox.dataset.title;

                checkCell.appendChild(checkbox);
                row.appendChild(checkCell);
                row.appendChild(textCell);
                tbody.appendChild(row);
            });

            table.appendChild(tbody);
            playlistItemsEl.appendChild(table);
            playlistItemsEl.addEventListener("change", updateSelectButtons);
            updateSelectButtons();

            playlistSection.style.display = "block";
            downloadSelectedButton.style.display = "inline-block";
            loadPlaylistButton.style.display = "none";
            selectAllButton.style.display = "inline-block";
            deselectAllButton.style.display = "inline-block";
            downloadStatusSection.style.display = "none";
            urlInputSection.style.display = "block";
            urlInputs.forEach(input => {
                input.style.display = "none";
            });
        } catch (error) {
            console.error("Error al cargar playlist", error);
            downloadStatusText.textContent = "Error al cargar playlist";
            urlInputSection.style.display = "block";
        }

        spinner.style.display = "none";
    }

    function startStatusPolling() {
        stopStatusPolling();
        cancelDownloadButton.style.display = "inline-block";
        downloadStatusTitle.style.display = "block";
        mainMenu.style.display = "none";
        urlInputSection.style.display = "none";
        downloadStatusSection.style.display = "block";
        statusTimer = setInterval(async () => {
            try {
                const status = await pywebview.api.get_status();
                if (!status || !status.state) return;
                if (status.state === "running") {
                    downloadStatusText.textContent = status.message || "Descargando...";
                    spinner.style.display = "block";
                } else {
                    downloadStatusText.textContent = status.message || "Listo";
                    spinner.style.display = "none";
                    cancelDownloadButton.style.display = "none";
                    stopStatusPolling();
                    setTimeout(backToMenu, 3000);
                }
            } catch (e) {
                console.error("Error al leer estado", e);
            }
        }, 1000);
    }

    function stopStatusPolling() {
        if (statusTimer) {
            clearInterval(statusTimer);
            statusTimer = null;
        }
    }

    async function downloadSelected() {
        const selected = [];
        const checkboxes = playlistItemsEl.querySelectorAll("input[type='checkbox']");
        checkboxes.forEach(cb => {
            if (cb.checked) {
                selected.push({ url: cb.dataset.url, title: cb.dataset.title });
            }
        });
        if (selected.length === 0) {
            downloadStatusText.textContent = "Selecciona al menos un video";
            downloadStatusSection.style.display = "block";
            return;
        }

        const dirName = playlistDirInput.value.trim() || playlistTitle || "";
        downloadStatusSection.style.display = "block";
        downloadStatusText.textContent = "Iniciando descarga...";
        spinner.style.display = "block";

        try {
            const result = await pywebview.api.download_selected({
                format: downloadType,
                dir: dirName,
                items: selected,
            });
            if (typeof result === "string" && result.toLowerCase().includes("error")) {
                downloadStatusText.textContent = result;
                spinner.style.display = "none";
                return;
            }
            startStatusPolling();
        } catch (error) {
            console.error("Error en la descarga", error);
            downloadStatusText.textContent = "Error en la descarga";
            spinner.style.display = "none";
        }
    }

    async function cancelDownload() {
        try {
            await pywebview.api.cancel_download();
        } catch (e) {
            console.error("Error al cancelar", e);
        }
    }

    function updateSelectButtons() {
        const checkboxes = playlistItemsEl.querySelectorAll("input[type='checkbox']");
        if (checkboxes.length === 0) {
            selectAllButton.disabled = true;
            deselectAllButton.disabled = true;
            return;
        }
        const total = checkboxes.length;
        const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
        selectAllButton.disabled = checked === total;
        deselectAllButton.disabled = checked === 0;
    }

    function selectAll(flag) {
        const checkboxes = playlistItemsEl.querySelectorAll("input[type='checkbox']");
        checkboxes.forEach(cb => {
            cb.checked = flag;
        });
        updateSelectButtons();
    }

    document.getElementById("mp3-btn").addEventListener("click", () => showUrlInput("mp3"));
    document.getElementById("playlist-mp3-btn").addEventListener("click", () => showUrlInput("playlist_mp3"));
    document.getElementById("mp4-btn").addEventListener("click", () => showUrlInput("mp4"));
    document.getElementById("playlist-mp4-btn").addEventListener("click", () => showUrlInput("playlist_mp4"));
    pasteButton.addEventListener("click", pasteUrl);
    downloadButton.addEventListener("click", startDownload);
    loadPlaylistButton.addEventListener("click", loadPlaylist);
    downloadSelectedButton.addEventListener("click", downloadSelected);
    cancelDownloadButton.addEventListener("click", cancelDownload);
    selectAllButton.addEventListener("click", () => selectAll(true));
    deselectAllButton.addEventListener("click", () => selectAll(false));
    backButton.addEventListener("click", backToMenu);
    videoUrlInput.addEventListener("input", updateDownloadButton);
});
