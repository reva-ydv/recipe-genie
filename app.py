from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load and preprocess data
data = pd.read_csv("cleaned_chatbot.csv")

def clean_ingredient(ingredient_list):
    cleaned_ingredients = []
    for ing in eval(ingredient_list):
        ing = re.sub(r'^\s*\d+[\d\s\-/.,]*', '', ing)
        ing = re.sub(r'\([^)]*\)', '', ing)
        ing = ing.strip()
        cleaned_ingredients.append(ing)
    return cleaned_ingredients

data['Ingredient_Names'] = data['Ingredients'].apply(clean_ingredient)

allergen_substitutes = {
    'peanut': 'sunflower seed butter',
    'tree nut': 'seeds',
    'milk': 'almond milk',
    'egg': 'flaxseed meal',
    'wheat': 'gluten-free flour',
    'soy': 'coconut aminos',
    'fish': 'tofu',
    'shellfish': 'tofu'
}

def replace_allergens(ingredients, allergen_substitutes):
    new_ingredients = []
    for ing in ingredients:
        for allergen, substitute in allergen_substitutes.items():
            if allergen in ing:
                ing = substitute
                break
        new_ingredients.append(ing)
    return new_ingredients

def update_dataset_allergens(data, allergen_substitutes):
    updated_ingredients = []
    for ingredients in data['Ingredient_Names']:
        new_ingredients = replace_allergens(ingredients, allergen_substitutes)
        updated_ingredients.append(new_ingredients)
    data['Updated_Ingredients'] = updated_ingredients
    data['Updated_Ingredient_Str'] = data['Updated_Ingredients'].apply(lambda x: ' '.join(x))
    return data

data = update_dataset_allergens(data, allergen_substitutes)
vectorizer = TfidfVectorizer()
X_updated = vectorizer.fit_transform(data['Updated_Ingredient_Str'])

def recommend_recipes(user_ingredients, data, vectorizer, X_updated):
    user_ingredients_str = ' '.join(user_ingredients)
    user_vec = vectorizer.transform([user_ingredients_str])
    similarities = cosine_similarity(user_vec, X_updated)
    sorted_indices = similarities[0].argsort()[::-1]
    return sorted_indices

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_ingredients = request.json.get('ingredients', [])
    if not user_ingredients:
        return jsonify({'error': 'No ingredients provided'}), 400

    replaced_ingredients = replace_allergens(user_ingredients, allergen_substitutes)
    sorted_indices = recommend_recipes(replaced_ingredients, data, vectorizer, X_updated)

    recommendations = []
    for idx in sorted_indices[:5]:  # Get top 5 recommendations
        recipe = data.iloc[idx]
        displayed_ingredients = replace_allergens(recipe['Ingredient_Names'], allergen_substitutes)
        recommendations.append({
            'title': recipe['Title'],
            'ingredients': displayed_ingredients,
            'instructions': recipe['Instructions']
        })

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
