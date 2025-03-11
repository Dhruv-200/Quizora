let questionCount = 0;

function addQuestion() {
    questionCount++;
    const questionHtml = `
        <div class="question" id="question-${questionCount}">
            <h3>Question ${questionCount}</h3>
            <div class="form-group">
                <label for="question-${questionCount}-text">Question Text</label>
                <input type="text" id="question-${questionCount}-text" name="question-${questionCount}-text" required>
            </div>
            <div class="options-container">
                <div class="form-group">
                    <label for="question-${questionCount}-option-1">Option 1</label>
                    <input type="text" id="question-${questionCount}-option-1" name="question-${questionCount}-option-1" required>
                    <input type="radio" name="question-${questionCount}-correct" value="1" required>
                </div>
                <div class="form-group">
                    <label for="question-${questionCount}-option-2">Option 2</label>
                    <input type="text" id="question-${questionCount}-option-2" name="question-${questionCount}-option-2" required>
                    <input type="radio" name="question-${questionCount}-correct" value="2" required>
                </div>
                <div class="form-group">
                    <label for="question-${questionCount}-option-3">Option 3</label>
                    <input type="text" id="question-${questionCount}-option-3" name="question-${questionCount}-option-3" required>
                    <input type="radio" name="question-${questionCount}-correct" value="3" required>
                </div>
                <div class="form-group">
                    <label for="question-${questionCount}-option-4">Option 4</label>
                    <input type="text" id="question-${questionCount}-option-4" name="question-${questionCount}-option-4" required>
                    <input type="radio" name="question-${questionCount}-correct" value="4" required>
                </div>
            </div>
        </div>
    `;
    document.getElementById('questions-container').insertAdjacentHTML('beforeend', questionHtml);
}

document.getElementById('add-question').addEventListener('click', addQuestion);

document.getElementById('quiz-form').addEventListener('submit', function(e) {
    e.preventDefault();
    if (questionCount < 10) {
        alert('Please add at least 10 questions to the quiz.');
        return;
    }
    
    const formData = new FormData(this);
    fetch('/create_quiz', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Quiz created successfully!');
            window.location.href = '/admin';
        } else {
            alert('Error creating quiz. Please try again.');
        }
    });
});

// Add initial 10 questions
for (let i = 0; i < 10; i++) {
    addQuestion();
}