document.addEventListener('DOMContentLoaded', function() {
    let userIngredients = [];
    let recipes = [];
    let currentRecipeIndex = 0;

    // Show initial instructions
    addMessage('Welcome! Enter your ingredients one by one. Type "done" when you are ready to generate recipes.', 'bot');

    document.getElementById('send-btn').addEventListener('click', function() {
        handleUserInput();
    });

    document.getElementById('user-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            handleUserInput();
        }
    });

    function handleUserInput() {
        const userInput = document.getElementById('user-input').value.trim().toLowerCase();
        if (userInput === '') return;

        if (userInput === 'yes' && recipes.length > 0) {
            displayNextRecipe();
        } else if (userInput === 'no') {
            addMessage('Okay, happy cooking :)', 'bot');
        } else if (userInput === 'done') {
            if (userIngredients.length === 0) {
                addMessage('Please enter some ingredients first.', 'bot');
            } else {
                fetch('/recommend', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ingredients: userIngredients })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        addMessage(data.error, 'bot');
                    } else {
                        recipes = data;
                        currentRecipeIndex = 0;
                        if (recipes.length > 0) {
                            displayNextRecipe();
                        } else {
                            addMessage('No recipes found for the given ingredients.', 'bot');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('Sorry, something went wrong. Please try again later.', 'bot');
                });
            }
            userIngredients = [];
        } else {
            userIngredients.push(userInput);
            addMessage(`Added ingredient: ${userInput}`, 'user');
        }

        document.getElementById('user-input').value = '';
    }

    function displayNextRecipe() {
        if (currentRecipeIndex < recipes.length) {
            const recipe = recipes[currentRecipeIndex];
            addMessage(`<b>Recipe Title:</b> ${recipe.title}`, 'bot');
            addMessage(`<b>Ingredients:</b> ${recipe.ingredients.join(', ')}`, 'bot');
            addMessage(`<b>Instructions:</b> ${recipe.instructions}`, 'bot');
            currentRecipeIndex++;
            if (currentRecipeIndex < recipes.length) {
                addMessage('Do you want to see the next recipe? (yes/no)', 'bot');
            } else {
                addMessage('No more recipes available.', 'bot');
            }
        }
    }

    function addMessage(text, sender) {
        const chatWindow = document.getElementById('chat-window');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        const messageText = document.createElement('p');
        messageText.innerHTML = text;
        messageElement.appendChild(messageText);
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to bottom
    }
});
