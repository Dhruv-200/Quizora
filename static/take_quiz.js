document.getElementById('quiz-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    fetch('/submit_quiz', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayResults(data.results);
        } else {
            alert('Error submitting quiz. Please try again.');
        }
    });
});

function displayResults(results) {
    const questions = document.querySelectorAll('.question');
    let score = 0;

    questions.forEach((question, index) => {
        const options = question.querySelectorAll('input[type="radio"]');
        const result = results[index];

        options.forEach(option => {
            const label = option.nextElementSibling;
            if (option.value == result.correct_option) {
                label.classList.add('correct-answer');
            } else if (option.checked && option.value != result.correct_option) {
                label.classList.add('wrong-answer');
            }
            option.disabled = true;
        });

        if (result.is_correct) {
            score++;
        }
    });

    const scoreElement = document.createElement('div');
    scoreElement.classList.add('quiz-score');
    scoreElement.textContent = `Your score: ${score} / ${questions.length}`;
    document.getElementById('quiz-form').appendChild(scoreElement);
}