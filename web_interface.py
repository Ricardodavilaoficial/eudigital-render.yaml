from flask import render_template_string


def html_index():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Eu Digital</title>
    </head>
    <body>
        <h1>🎤 Fale com o Eu Digital</h1>
        <button id="startBtn">🎙️ Começar Gravação</button>
        <p id="status">Aguardando interação...</p>
        <audio id="responseAudio" controls></audio>

        <script>
            let mediaRecorder;
            let audioChunks = [];

            const startBtn = document.getElementById("startBtn");
            const statusPara = document.getElementById("status");
            const responseAudio = document.getElementById("responseAudio");

            startBtn.onclick = async () => {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                const analyser = audioContext.createAnalyser();
                source.connect(analyser);
                analyser.fftSize = 512;

                const dataArray = new Uint8Array(analyser.frequencyBinCount);

                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                statusPara.textContent = "🎙️ Gravando…";

                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

                mediaRecorder.onstop = async () => {
                    statusPara.textContent = "⏳ Enviando para IA…";

                    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                    const formData = new FormData();
                    formData.append("file", audioBlob, "gravacao.webm");

                    try {
                        const response = await fetch("/audio", {
                            method: "POST",
                            body: formData,
                        });

                        if (!response.ok) {
                            console.error("❌ Erro na resposta da IA:", response.statusText);
                            alert("Erro ao processar o áudio.");
                            return;
                        }

                        const audioBuffer = await response.blob();
                        responseAudio.src = URL.createObjectURL(audioBuffer);
                        responseAudio.play();
                        statusPara.textContent = "✅ Resposta recebida!";
                    } catch (err) {
                        console.error("❌ Erro na requisição:", err);
                        alert("Erro ao enviar áudio.");
                        statusPara.textContent = "⚠️ Erro ao enviar.";
                    }
                };

                mediaRecorder.start();

                let silentSeconds = 0;
                const silenceThreshold = 0.02;
                const checkInterval = 200;

                const checkSilence = setInterval(() => {
                    analyser.getByteFrequencyData(dataArray);
                    const avgVolume = dataArray.reduce((a, b) => a + b) / dataArray.length / 256;

                    if (avgVolume < silenceThreshold) {
                        silentSeconds += checkInterval;
                        if (silentSeconds >= 5000) {
                            clearInterval(checkSilence);
                            mediaRecorder.stop();
                            audioContext.close();
                            statusPara.textContent = "🛑 Silêncio detectado. Gravação encerrada.";
                        }
                    } else {
                        silentSeconds = 0;
                    }
                }, checkInterval);
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)
