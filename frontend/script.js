document.getElementById("analyzeButton").addEventListener("click", analyzeStory);

function getSelectedOptions() {
    return {
        totalWords: document.getElementById("totalWords").checked,
        differentWords: document.getElementById("differentWords").checked,
        typeTokenRatio: document.getElementById("typeTokenRatio").checked,
        numMorphemes: document.getElementById("numMorphemes").checked,
        numClauses: document.getElementById("numClauses").checked,
        subordinateClauses: document.getElementById("subordinateClauses").checked,
        subordinationIndex: document.getElementById("subordinationIndex").checked,
        verbErrors: document.getElementById("verbErrors").checked,
        verbErrorsPerClause: document.getElementById("verbErrorsPerClause").checked,
        wordChoiceErrors: document.getElementById("wordChoiceErrors").checked,
        wordChoiceErrorsPerWord: document.getElementById("wordChoiceErrorsPerWord").checked,
        storyGrammar: document.getElementById("storyGrammar").checked,
        cohesion: document.getElementById("cohesion").checked
    };
}

async function analyzeStory() {
    const textInput = document.getElementById("storyInput").value.trim();
    const selectedOptions = getSelectedOptions();

    if (!textInput) {
        alert("Please enter a story to analyze.");
        return;
    }

    if (Object.values(selectedOptions).every(value => !value)) {
        alert("Please select at least one analysis option.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: textInput, options: selectedOptions })
        });

        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        
        let outputHtml = `<h3>📝 Analysis</h3>`;

        // Process ALL selected options (AI & Non-AI)
        if (data.results) {
            outputHtml += "<ul class='analysis-list'>";
            for (const key in selectedOptions) {

                if (key === "storyGrammar" || key === "cohesion") continue;

                if (selectedOptions[key]) {  //  Only show selected results
                    let displayValue = data.results[key] !== undefined ? data.results[key] : "N/A";
                    outputHtml += `<li><strong>${formatKey(key)}:</strong> ${displayValue}</li>`;
                }
            }
            outputHtml += "</ul>";
        }

        // Process AI Analysis (Story Grammar & Cohesion)
        if (selectedOptions.storyGrammar && data.results.story_grammar) {
            outputHtml += `<h3>📖 Story Grammar Elements</h3><ul class='analysis-list'>`;
            for (const key in data.results.story_grammar) {
                outputHtml += `<li><strong>${formatKey(key)}:</strong> ${data.results.story_grammar[key]}</li>`;
            }
            outputHtml += "</ul>";
        }

        if (selectedOptions.cohesion && data.results.cohesion) {
            outputHtml += `<h3>🔗 Cohesion Analysis</h3>`;
            if (typeof data.results.cohesion === "object") {
                outputHtml += "<ul class='analysis-list'>";
                for (const key in data.results.cohesion) {
                    outputHtml += `<li><strong>${formatKey(key)}:</strong> ${data.results.cohesion[key]}</li>`;
                }
                outputHtml += "</ul>";
            } else {
                outputHtml += `<p>${data.results.cohesion}</p>`;
            }
        }

        // Update existing accuracy field (prevent duplicates)
        document.getElementById("result").innerHTML = outputHtml;
        document.getElementById("accuracy").textContent = data.accuracy || "N/A";

    } catch (error) {
        console.error("Error:", error);
        document.getElementById("result").innerHTML = "<p class='error-msg'>🚨 Server error. Ensure Flask is running.</p>";
    }
}

/**
 * Helper function: Format keys into readable text.
 */
function formatKey(key) {
    return key.replace(/([A-Z])/g, ' $1') // Add space before capital letters
              .replace(/^./, str => str.toUpperCase()) // Capitalize first letter
              .replace(/_/g, ' '); // Replace underscores with spaces
}
