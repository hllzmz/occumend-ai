// --- 1. CONSTANTS AND VARIABLES ---
const questions = [
    { cat: 'R', text: 'Test the quality of parts before shipment' }, { cat: 'R', text: 'Lay brick or tile' }, { cat: 'R', text: 'Work on an offshore oil-drilling rig' }, { cat: 'R', text: 'Assemble electronic parts' }, { cat: 'R', text: 'Operate a grinding machine in a factory' }, { cat: 'R', text: 'Fix a broken faucet' }, { cat: 'R', text: 'Assemble products in a factory' }, { cat: 'R', text: 'Install flooring in houses' },
    { cat: 'I', text: 'Study the structure of the human body' }, { cat: 'I', text: 'Study animal behavior' }, { cat: 'I', text: 'Do research on plants or animals' }, { cat: 'I', text: 'Develop a new medical treatment or procedure' }, { cat: 'I', text: 'Conduct biological research' }, { cat: 'I', text: 'Study whales and other types of marine life' }, { cat: 'I', text: 'Work in a biology lab' }, { cat: 'I', text: 'Make a map of the bottom of an ocean' },
    { cat: 'A', text: 'Conduct a musical choir' }, { cat: 'A', text: 'Direct a play' }, { cat: 'A', text: 'Design artwork for magazines' }, { cat: 'A', text: 'Write a song' }, { cat: 'A', text: 'Write books or plays' }, { cat: 'A', text: 'Play a musical instrument' }, { cat: 'A', text: 'Perform stunts for a movie or television show' }, { cat: 'A', text: 'Design sets for plays' },
    { cat: 'S', text: 'Give career guidance to people' }, { cat: 'S', text: 'Do volunteer work at a non-profit organization' }, { cat: 'S', text: 'Help people who have problems with drugs or alcohol' }, { cat: 'S', text: 'Teach an individual an exercise routine' }, { cat: 'S', text: 'Help people with family-related-problems' }, { cat: 'S', text: 'Supervise the activities of children at a camp' }, { cat: 'S', text: 'Teach children how to read' }, { cat: 'S', text: 'Help elderly people with their daily activities' },
    { cat: 'E', text: 'Sell restaurant franchises to individuals' }, { cat: 'E', text: 'Sell merchandise at a department store' }, { cat: 'E', text: 'Manage the operations of a hotel' }, { cat: 'E', text: 'Operate a beauty salon or barber shop' }, { cat: 'E', text: 'Manage a department within a large company' }, { cat: 'E', text: 'Manage a clothing store' }, { cat: 'E', text: 'Sell houses' }, { cat: 'E', text: 'Run a toy store' },
    { cat: 'C', text: 'Generate the monthly payroll checks for an office' }, { cat: 'C', text: 'Inventory supplies using a hand-held computer' }, { cat: 'C', text: 'Use a computer program to generate customer bills' }, { cat: 'C', text: 'Maintain employee records' }, { cat: 'C', text: 'Compute and record statistical and other numerical data' }, { cat: 'C', text: 'Operate a calculator' }, { cat: 'C', text: 'Handle customers\' bank transactions' }, { cat: 'C', text: 'Keep shipping and receiving records' }
];

const steps = ['R', 'I', 'A', 'S', 'E', 'C'];
let currentStep = 0;
let userAnswers = {}; // Store all answers

// --- 2. DOM ELEMENTS ---
// DOM elements will be assigned after the DOM is loaded.
let surveyBody, backBtn, nextBtn, progressBar, validationMsg, formContainer, resultsContainer, chatForm, chatInput, chatMessages;

let userProfileSummary = '';
let recommendationsData = [];

// --- 3. FUNCTIONS ---

function renderStep(stepIndex) {
    const category = steps[stepIndex];
    const stepQuestions = questions.filter(q => q.cat === category);

    surveyBody.innerHTML = '';
    stepQuestions.forEach(q => {
        const qIndex = questions.indexOf(q);
        const row = document.createElement('tr');
        row.className = `cat-${q.cat.toLowerCase()}`;
        row.id = `q-row-${qIndex}`;

        let rowHTML = `<td>${q.text}</td>`;
        for (let i = 1; i <= 5; i++) {
            const isChecked = userAnswers[qIndex] === i.toString() ? 'checked' : '';
            rowHTML += `<td><input type="radio" name="q${qIndex}" value="${i}" data-q-index="${qIndex}" ${isChecked}></td>`;
        }
        row.innerHTML = rowHTML;
        surveyBody.appendChild(row);
    });
    updateUI();
}

function updateUI() {
    const progress = (currentStep / steps.length) * 100;
    progressBar.style.width = `${progress}%`;
    progressBar.textContent = `${Math.round(progress)}%`;

    backBtn.style.visibility = currentStep === 0 ? 'hidden' : 'visible';
    nextBtn.textContent = currentStep === steps.length - 1 ? 'Get Results' : 'Next';
}

function validateStep() {
    const currentQuestions = questions.filter(q => q.cat === steps[currentStep]);
    let allAnswered = true;
    validationMsg.style.visibility = 'hidden';

    currentQuestions.forEach(q => {
        const qIndex = questions.indexOf(q);
        const row = document.getElementById(`q-row-${qIndex}`);
        row.classList.remove('question-error');

        if (!userAnswers[qIndex]) {
            allAnswered = false;
            row.classList.add('question-error');
        }
    });

    if (!allAnswered) {
        validationMsg.style.visibility = 'visible';
    }
    return allAnswered;
}

async function goToNext() {
    if (!validateStep()) return;

    if (currentStep < steps.length - 1) {
        currentStep++;
        await fadeTransition(renderStep, currentStep);
    } else {
        await submitAndShowResults();
    }
}

async function goToBack() {
    if (currentStep > 0) {
        currentStep--;
        await fadeTransition(renderStep, currentStep);
    }
}

function fadeTransition(updateFunction, ...args) {
    return new Promise(resolve => {
        formContainer.classList.add('fade-out');
        setTimeout(() => {
            updateFunction(...args);
            formContainer.classList.remove('fade-out');
            resolve();
        }, 400);
    });
}

async function submitAndShowResults() {
    nextBtn.disabled = true;
    nextBtn.textContent = "Calculating...";

    formContainer.classList.add('fade-out');
    setTimeout(() => {
        formContainer.style.display = 'none';
        resultsContainer.innerHTML = '<h2>Calculating Results...</h2>';
        resultsContainer.classList.add('visible');
    }, 400);

    const answersForBackend = { R: [], I: [], A: [], S: [], E: [], C: [] };
    for (const qIndex in userAnswers) {
        const category = questions[qIndex].cat;
        answersForBackend[category].push(parseInt(userAnswers[qIndex]));
    }

    try {
        await new Promise(resolve => setTimeout(resolve, 450));
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(answersForBackend),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const data = await response.json();
        renderResults(data, answersForBackend);

    } catch (error) {
        resultsContainer.innerHTML = '<h2>An error occurred. Please try again.</h2>';
        console.error('Detailed Error:', error);
    }
}

function renderResults(data, answersForBackend) {
    recommendationsData = data.recommendations;

    const riasecScores = {};
    for (const cat in answersForBackend) {
        const scores = answersForBackend[cat];
        riasecScores[cat] = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(2) : 0;
    }
    const topJobs = recommendationsData.slice(0, 3).map(rec => rec.Title).join(', ');
    userProfileSummary = `My RIASEC interest scores are: Realistic: ${riasecScores.R}, Investigative: ${riasecScores.I}, Artistic: ${riasecScores.A}, Social: ${riasecScores.S}, Enterprising: ${riasecScores.E}, Conventional: ${riasecScores.C}. The top recommended jobs for me were: ${topJobs}.`;

    let resultsHtml = '<h2>Your Results</h2>';
    resultsHtml += `
        <div class="charts-container">
            <div class="chart-wrapper">
                <h3>Your Interest Profile</h3>
                <img src="${data.chart_images.radar}" alt="Your Interest Profile Radar Chart">
            </div>
            <div class="chart-wrapper">
                <h3>Top Job Matches</h3>
                <img src="${data.chart_images.bar}" alt="Top Job Matches Bar Chart">
            </div>
        </div>
    `;
    resultsHtml += '<h3>Recommendations List</h3><table class="results-table"><thead><tr><th>Occupation</th><th>Career Cluster</th><th>Similarity</th><th>Details</th></tr></thead><tbody>';
    recommendationsData.forEach((rec, index) => {
        resultsHtml += `
            <tr class="result-row">
                <td>${rec.Title}</td>
                <td>${rec.cluster_name}</td>
                <td>${(rec.similarity * 100).toFixed(2)}%</td>
                <td><button class="details-btn" data-row-index="${index}">Details</button></td>
            </tr>
            <tr id="details-row-${index}" class="details-row hidden"><td colspan="4">
                <div class="details-content">
                    <div><h4>Top 5 Required Knowledge</h4><ul>${rec.knowledge.map(item => `<li>${item}</li>`).join('') || '<li>N/A</li>'}</ul></div>
                    <div><h4>Top 5 Required Skills</h4><ul>${rec.skills.map(item => `<li>${item}</li>`).join('') || '<li>N/A</li>'}</ul></div>
                    <div><h4>Top 5 Required Abilities</h4><ul>${rec.abilities.map(item => `<li>${item}</li>`).join('') || '<li>N/A</li>'}</ul></div>
                </div>
            </td></tr>`;
    });
    resultsHtml += '</tbody></table>';

    resultsContainer.innerHTML = resultsHtml;
    document.getElementById('chat-container').classList.remove('hidden');
    addChatMessage("Hello! I'm your AI career advisor OccumendAI. Feel free to ask me anything about your results or the recommended jobs.", "bot-message");
}

function addChatMessage(message, className) {
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${className}`;
    if (className === 'bot-message') {
        messageElement.innerHTML = marked.parse(message);
    } else {
        messageElement.textContent = message;
    }
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageElement;
}

// --- 4. EVENT LISTENERS & INITIALIZATION ---

document.addEventListener('DOMContentLoaded', () => {
    // Assign DOM elements
    surveyBody = document.getElementById('survey-body');
    backBtn = document.getElementById('nav-back');
    nextBtn = document.getElementById('nav-next');
    progressBar = document.getElementById('progress-bar');
    validationMsg = document.getElementById('validation-message');
    formContainer = document.getElementById('riasec-form-container');
    resultsContainer = document.getElementById('results');
    chatForm = document.getElementById('chat-form');
    chatInput = document.getElementById('chat-input');
    chatMessages = document.getElementById('chat-messages');

    // Survey navigation events
    nextBtn.addEventListener('click', goToNext);
    backBtn.addEventListener('click', goToBack);

    // Survey answer event
    surveyBody.addEventListener('change', event => {
        if (event.target.type === 'radio') {
            const qIndex = event.target.getAttribute('data-q-index');
            userAnswers[qIndex] = event.target.value;
            const row = document.getElementById(`q-row-${qIndex}`);
            if (row.classList.contains('question-error')) {
                row.classList.remove('question-error');
                if (document.querySelectorAll('.question-error').length === 0) {
                    validationMsg.style.visibility = 'hidden';
                }
            }
        }
    });

    // Event listener for the "Details" button in the results table
    resultsContainer.addEventListener('click', event => {
        if (event.target.classList.contains('details-btn')) {
            const rowIndex = event.target.getAttribute('data-row-index');
            const detailsRow = document.getElementById(`details-row-${rowIndex}`);
            if (detailsRow) {
                detailsRow.classList.toggle('hidden');
            }
        }
    });

    document.getElementById('riasec-form').addEventListener('submit', e => e.preventDefault());

    // Chat events
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    chatForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const userQuestion = chatInput.value.trim();
        if (!userQuestion) return;
        addChatMessage(userQuestion, 'user-message');
        chatInput.value = '';
        chatInput.style.height = 'auto';
        const typingIndicator = addChatMessage("Typing...", 'bot-message');
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userQuestion, profile_summary: userProfileSummary }),
            });
            const data = await response.json();
            typingIndicator.remove();
            if (data.answer) {
                addChatMessage(data.answer, 'bot-message');
            } else {
                addChatMessage(data.error || 'Sorry, something went wrong.', 'bot-message');
            }
        } catch (error) {
            typingIndicator.remove();
            addChatMessage('I seem to be having trouble connecting. Please try again later.', 'bot-message');
        }
    });

    // --- Initial Load ---
    renderStep(currentStep);
});