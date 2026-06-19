window.onload = function () {

    document.getElementById("file1").addEventListener("change", function () {

        document.getElementById("file1-name").innerText =
            this.files[0]?.name || "No file chosen";
    });
    document.getElementById("file2").addEventListener("change", function () {

        document.getElementById("file2-name").innerText =
            this.files[0]?.name || "No file chosen";
    });

};
function highlightContent(
    text,
    matchedSentences,
    commonWords,
    fileNumber
) {

    let highlightedText = text;
    matchedSentences.forEach(match => {
        let sentence =
            fileNumber === 1
            ? match.sentence1
            : match.sentence2;
        if (sentence.length > 0) {
            highlightedText =
                highlightedText.replace(
                    sentence,
                    `###START###${sentence}###END###`
                );
        }
    });

    commonWords.forEach(word => {
        let regex = new RegExp(
            `\\b${word}\\b`,
            "gi"
        );
        highlightedText =
            highlightedText.replace(
                regex,
                `<span class="word-highlight">${word}</span>`
            );
    });

    highlightedText =
        highlightedText.replace(
            /###START###/g,
            `<mark class="sentence-highlight">`
        );
    highlightedText =
        highlightedText.replace(
            /###END###/g,
            `</mark>`
        );
    return highlightedText;
}
async function checkPlagiarism() {
    let file1 = document.getElementById("file1").files[0];
    let file2 = document.getElementById("file2").files[0];
    if (!file1 || !file2) {
        alert("Please upload both files");
        return;
    }
    document.getElementById("name1").innerText =
        "File 1: " + file1.name;

    document.getElementById("name2").innerText =
        "File 2: " + file2.name;

    document.getElementById("result").innerHTML = `
        <h3>Checking plagiarism...</h3>
    `;
    let formData = new FormData();
    formData.append("file1", file1);
    formData.append("file2", file2);
    try {
        let response = await fetch("/check", {

            method: "POST",
            body: formData
        });
        let data = await response.json();
        if (data.error) {
            document.getElementById("result").innerHTML = `
                <span style="color:red;">
                    ${data.error}
                </span>
            `;
            return;
        }
        document.getElementById("result").innerHTML = `
            <h2>Result</h2>
            <p>
                <b>Plagiarism:</b>
                ${data.similarity}%
            </p>
            <div class="progress-container">

                <div class="progress-bar"
                    style="width:${data.similarity}%">

                ${data.similarity}%
                </div>
            </div>  
            <p>
                <b>Status:</b>
                ${data.status}
            </p>
            <p>
                <b>${data.file1_name}</b>
                Words: ${data.words1}
            </p>
            <p>
                <b>${data.file2_name}</b>
                Words: ${data.words2}
            </p>
            <p>
                <b>Matched Sentences:</b>
                ${data.matched_sentences.length}
            </p>
        `;
        document.getElementById("preview1").innerHTML =
            highlightContent(
                data.text1,
                data.matched_sentences,
                data.common_words,
            1
            );
        document.getElementById("preview2").innerHTML =
            highlightContent(
                data.text2,
                data.matched_sentences,
                data.common_words,
             2
            );
        document.getElementById("exportBtn")
            .style.display = "block";
        document.querySelector(".preview-container")
            .scrollIntoView({
                behavior: "smooth"
            });
    }
    catch (error) {
        document.getElementById("result").innerHTML = `
            <span style="color:red;">
                Something went wrong.
            </span>
        `;
        console.log(error);
    }
}
function exportPDF() {
    window.location.href = "/export";
}