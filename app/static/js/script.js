// --- 1. CONSTANTS AND VARIABLES ---
const questions = [
    { cat: 'R', text: 'Build kitchen cabinets' },
    { cat: 'R', text: 'Lay brick or tile' },
    { cat: 'R', text: 'Repair household appliances' },
    { cat: 'R', text: 'Raise fish in a fish hatchery' },
    { cat: 'R', text: 'Assemble electronic parts' },
    { cat: 'R', text: 'Drive a truck to deliver packages to offices and homes' },
    { cat: 'R', text: 'Test the quality of parts before shipment' },
    { cat: 'R', text: 'Repair and install locks' },
    { cat: 'R', text: 'Set up and operate machines to make products' },
    { cat: 'R', text: 'Put out forest fires' },

    { cat: 'I', text: 'Develop a new medicine' },
    { cat: 'I', text: 'Study ways to reduce water pollution' },
    { cat: 'I', text: 'Conduct chemical experiments' },
    { cat: 'I', text: 'Study the movement of planets' },
    { cat: 'I', text: 'Examine blood samples using a microscope' },
    { cat: 'I', text: 'Investigate the cause of a fire' },
    { cat: 'I', text: 'Develop a way to better predict the weather' },
    { cat: 'I', text: 'Work in a biology lab' },
    { cat: 'I', text: 'Invent a replacement for sugar' },
    { cat: 'I', text: 'Do laboratory tests to identify diseases' },

    { cat: 'A', text: 'Write books or plays' },
    { cat: 'A', text: 'Play a musical instrument' },
    { cat: 'A', text: 'Compose or arrange music' },
    { cat: 'A', text: 'Draw pictures' },
    { cat: 'A', text: 'Create special effects for movies' },
    { cat: 'A', text: 'Paint sets for plays' },
    { cat: 'A', text: 'Write scripts for movies or television shows' },
    { cat: 'A', text: 'Perform jazz or tap dance' },
    { cat: 'A', text: 'Sing in a band' },
    { cat: 'A', text: 'Edit movies' },

    { cat: 'S', text: 'Teach an individual an exercise routine' },
    { cat: 'S', text: 'Help people with personal or emotional problems' },
    { cat: 'S', text: 'Give career guidance to people' },
    { cat: 'S', text: 'Perform rehabilitation therapy' },
    { cat: 'S', text: 'Do volunteer work at a non-profit organization' },
    { cat: 'S', text: 'Teach children how to play sports' },
    { cat: 'S', text: 'Teach sign language to people with hearing disabilities' },
    { cat: 'S', text: 'Help conduct a group therapy session' },
    { cat: 'S', text: 'Take care of children at a day-care center' },
    { cat: 'S', text: 'Teach a high-school class' },

    { cat: 'E', text: 'Buy and sell stocks and bonds' },
    { cat: 'E', text: 'Manage a retail store' },
    { cat: 'E', text: 'Operate a beauty salon or barber shop' },
    { cat: 'E', text: 'Manage a department within a large company' },
    { cat: 'E', text: 'Start your own business' },
    { cat: 'E', text: 'Negotiate business contracts' },
    { cat: 'E', text: 'Represent a client in a lawsuit' },
    { cat: 'E', text: 'Market a new line of clothing' },
    { cat: 'E', text: 'Sell merchandise at a department store' },
    { cat: 'E', text: 'Manage a clothing store' },

    { cat: 'C', text: 'Develop a spreadsheet using computer software' },
    { cat: 'C', text: 'Proofread records or forms' },
    { cat: 'C', text: 'Load computer software into a large computer network' },
    { cat: 'C', text: 'Operate a calculator' },
    { cat: 'C', text: 'Keep shipping and receiving records' },
    { cat: 'C', text: 'Calculate the wages of employees' },
    { cat: 'C', text: 'Inventory supplies using a hand-held computer' },
    { cat: 'C', text: 'Record rent payments' },
    { cat: 'C', text: 'Keep inventory records' },
    { cat: 'C', text: 'Stamp, sort, and distribute mail for an organization' }
];

const steps = ['R', 'I', 'A', 'S', 'E', 'C'];
const optionLabels = ['Dislike', 'Slightly Dislike', 'Neutral', 'Slightly Enjoy', 'Enjoy'];
let currentStep = 0;
let userAnswers = {}; // Store all answers

// --- 2. DOM ELEMENTS ---
// DOM elements will be assigned after the DOM is loaded.
let surveyBody, backBtn, nextBtn, progressBar, validationMsg, formContainer, resultsContainer, chatForm, chatInput, chatMessages, loaderContainer, scrollToTopBtn;

let userProfileSummary = '';
let recommendationsData = [];

// --- 3. FUNCTIONS ---

function renderStep(stepIndex) {
    const category = steps[stepIndex];
    const stepQuestions = questions.filter(q => q.cat === category);

    surveyBody.innerHTML = '';
    stepQuestions.forEach(q => {
        const qIndex = questions.indexOf(q);
        const card = document.createElement('div');
        card.className = `survey-question-card cat-${q.cat.toLowerCase()}`;
        card.id = `q-card-${qIndex}`;

        let optionsHTML = '';
        for (let i = 1; i <= 5; i++) {
            const isChecked = userAnswers[qIndex] === i.toString();
            const isSelected = isChecked ? 'selected' : '';
            optionsHTML += `
                <label class="survey-option ${isSelected}">
                    <input type="radio" name="q${qIndex}" value="${i}" data-q-index="${qIndex}" ${isChecked ? 'checked' : ''}>
                    <span class="option-label">${optionLabels[i - 1]}</span>
                </label>
            `;
        }

        card.innerHTML = `
            <p class="question-text">${q.text}</p>
            <div class="survey-options">
                ${optionsHTML}
            </div>
        `;
        surveyBody.appendChild(card);
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
        const card = document.getElementById(`q-card-${qIndex}`);
        card.classList.remove('question-error');

        if (!userAnswers[qIndex]) {
            allAnswered = false;
            card.classList.add('question-error');
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
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        await submitAndShowResults();
    }
}

async function goToBack() {
    if (currentStep > 0) {
        currentStep--;
        await fadeTransition(renderStep, currentStep);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function fadeTransition(updateFunction, ...args) {
    return new Promise(resolve => {
        // Disable buttons during transition
        nextBtn.disabled = true;
        backBtn.disabled = true;

        formContainer.classList.add('fade-out');
        setTimeout(() => {
            updateFunction(...args);
            // Focus the first input of the new step for accessibility
            const firstInput = surveyBody.querySelector('input[type="radio"]');
            if (firstInput) {
                firstInput.focus();
            }
            formContainer.classList.remove('fade-out');

            // Re-enable buttons after transition
            nextBtn.disabled = false;
            backBtn.disabled = false;
            resolve();
        }, 400);
    });
}

async function submitAndShowResults() {
    nextBtn.disabled = true;
    backBtn.disabled = true;

    formContainer.classList.add('fade-out');
    setTimeout(() => {
        formContainer.style.display = 'none';
        loaderContainer = document.querySelector('.loader-container');
        if (loaderContainer) loaderContainer.classList.remove('hidden');
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
        if (loaderContainer) loaderContainer.classList.add('hidden');
        resultsContainer.innerHTML = '<h2>An error occurred. Please try again.</h2>';
        console.error('Detailed Error:', error);
    }
}

function renderResults(data, answersForBackend) {
    recommendationsData = data.recommendations || [];

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
            <div class="chart-block">
                <h3>Your Interest Profile</h3>
                <div class="chart-wrapper">
                    <img src="${data.chart_images.radar}" alt="Your Interest Profile Radar Chart">
                </div>
            </div>
            <div class="chart-block">
                <h3>Top Job Matches</h3>
                <div class="chart-wrapper">
                    <img src="${data.chart_images.bar}" alt="Top Job Matches Bar Chart">
                </div>
            </div>
        </div>
    `;

    resultsHtml += '<h3>Recommendations List</h3><table class="results-table"><thead><tr><th>Occupation</th><th>Career Cluster</th><th>Similarity</th><th>Details</th></tr></thead><tbody>';
    recommendationsData.forEach((rec, index) => {
        const similarityPercentage = (rec.similarity * 100).toFixed(2);
        resultsHtml += `
            <tr class="result-row">
                <td data-label="Occupation">${rec.Title}</td>
                <td data-label="Career Cluster">${rec.cluster_name}</td>
                 <td data-label="Similarity">
                    <div class="similarity-row">
                        <div class="similarity-bar-container" title="Similarity: ${similarityPercentage}%">
                            <div class="similarity-bar" style="width: ${similarityPercentage}%;"></div>
                            <span>${similarityPercentage}%</span>
                        </div>
                        <div class="similarity-percentage">${similarityPercentage}%</div>
                    </div>
                </td>
                <td data-label="Details"><button class="details-btn" data-row-index="${index}">Details</button></td>
            </tr>
            <tr id="details-row-${index}" class="details-row hidden"><td colspan="4">
                <div class="details-content">
                    <div><h4>Top 5 Required Knowledge</h4><ul>${rec.knowledge && rec.knowledge.length ? rec.knowledge.map(item => `<li>${item}</li>`).join('') : '<li>N/A</li>'}</ul></div>
                    <div><h4>Top 5 Required Skills</h4><ul>${rec.skills && rec.skills.length ? rec.skills.map(item => `<li>${item}</li>`).join('') : '<li>N/A</li>'}</ul></div>
                    <div><h4>Top 5 Required Abilities</h4><ul>${rec.abilities && rec.abilities.length ? rec.abilities.map(item => `<li>${item}</li>`).join('') : '<li>N/A</li>'}</ul></div>
                </div>
            </td></tr>`;
    });
    resultsHtml += '</tbody></table>';

    const loaderContainer = document.querySelector('.loader-container');
    if (loaderContainer) loaderContainer.classList.add('hidden');

    resultsContainer.innerHTML = resultsHtml;
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.style.display = 'block';
        chatContainer.classList.remove('hidden');
    }
    addChatMessage("Hello! I'm your AI career advisor OccumendAI. Feel free to ask me anything about your results or the recommended jobs.", "bot-message");
    renderSuggestedQuestions();
}

function renderSuggestedQuestions() {
    const container = document.getElementById('suggested-questions-container');
    container.innerHTML = '';
    const suggestions = [
        "What are the daily tasks for a " + recommendationsData[0].Title + "?",
        "What skills do I need for a career in " + recommendationsData[1].Title + "?",
        "Tell me about my job interests profile.",
    ];

    suggestions.forEach(q => {
        const btn = document.createElement('button');
        btn.className = 'suggested-question';
        btn.textContent = q;
        container.appendChild(btn);
    });
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

            const currentCard = document.getElementById(`q-card-${qIndex}`);
            currentCard.querySelectorAll('.survey-option').forEach(opt => opt.classList.remove('selected'));
            event.target.closest('.survey-option').classList.add('selected');

            if (currentCard.classList.contains('question-error')) {
                currentCard.classList.remove('question-error');
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

    // Event listener for suggested questions
    document.getElementById('suggested-questions-container').addEventListener('click', event => {
        if (event.target.classList.contains('suggested-question')) {
            const questionText = event.target.textContent;
            chatInput.value = questionText;
            chatInput.style.height = 'auto';
            chatInput.style.height = (chatInput.scrollHeight) + 'px';
            chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
    });

    document.getElementById('riasec-form').addEventListener('submit', e => e.preventDefault());

    // Chat events
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    chatInput.addEventListener('keydown', function (event) {
        // Check if Enter is pressed without the Shift key
        if (event.key === 'Enter' && !event.shiftKey) {
            // Prevent default action (which is to add a new line)
            event.preventDefault();
            // Trigger the form's submit event
            chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
        // If Shift + Enter is pressed, the default browser behavior (adding a new line) will execute.
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