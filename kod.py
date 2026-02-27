from flask import Flask, render_template_string
import requests
import random

app = Flask(__name__)


reviews_list = [
    {"name": "Marek", "text": "Perfektný drink. Určite si ho dám znova.", "rating": 5},
    {"name": "Lucia", "text": "Veľmi osviežujúci, ideálny na leto.", "rating": 4},
    {"name": "Peter", "text": "Trochu silný, ale chuť výborná.", "rating": 4},
    {"name": "Zuzana", "text": "Nealko verzia ma milo prekvapila.", "rating": 5},
    {"name": "Tomáš", "text": "Za mňa priemer, ale pekne vyzerá.", "rating": 3},
    {"name": "Andrea", "text": "Mega sladký, presne ako mám rada.", "rating": 5},
    {"name": "Filip", "text": "Čakal som viac, ale dalo sa.", "rating": 3},
    {"name": "Natália", "text": "Výborne osviežujúce, odporúčam.", "rating": 4},
    {"name": "Kamil", "text": "Skvelé farby a chuť!", "rating": 5}
]

# Luxusné názvy drinkov
luxury_names = [
    "Sunset Royale", "Velvet Martini", "Golden Oasis",
    "Crystal Lagoon", "Midnight Bloom", "Starlight Mojito",
    "Aurora Spritz", "Moonlit Margarita", "Sapphire Collins",
    "Neon Nectar"
]

@app.route('/')
def home():
    try:
        response = requests.get("https://boozeapi.com/api/v1/cocktails", timeout=5)
        response.raise_for_status()
        raw = response.json()
        cocktails = raw.get("data", [])
    except Exception:
        cocktails = []

    # Pridanie recenzií, priemerného hodnotenia a luxusného názvu
    for i, drink in enumerate(cocktails):
        drink["luxury_name"] = luxury_names[i % len(luxury_names)]
        drink["reviews"] = random.sample(reviews_list, 4)
        drink["avg_rating"] = round(sum(r["rating"] for r in drink["reviews"]) / len(drink["reviews"]))
        ingredients = drink.get("ingredients", [])
        recipe_text = ""
        for item in ingredients[:6]:
            recipe_text += f"- {item.get('name','')} ({item.get('measure','')})\n"
        drink["recipe"] = recipe_text if recipe_text else "Recept momentálne nie je dostupný."

    # Zoradenie drinkov podľa priemerného hodnotenia pre top list
    top_drinks = sorted(cocktails, key=lambda x: x["avg_rating"], reverse=True)[:5]

    html_template = """
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="UTF-8">
        <title>Luxusné Koktaily</title>
        <style>
            body {
                margin:0; font-family:'Segoe UI', sans-serif;
                background: linear-gradient(120deg,#0a0a1f,#1a1a3d); color:white; overflow-x:hidden;
            }
            h1{
                text-align:center; font-size:80px; font-weight:900; text-transform:uppercase; letter-spacing:2px;
                color:#fff; text-shadow:0 0 10px #ff00cc,0 0 20px #00f7ff,0 0 30px #ff00cc,0 0 40px #00ff00;
                animation: pulse 2s infinite; margin:40px 0; cursor:pointer;
            }
            @keyframes pulse{
                0%,100%{ text-shadow:0 0 10px #ff00cc,0 0 20px #00f7ff,0 0 30px #ff00cc,0 0 40px #00ff00; }
                50%{ text-shadow:0 0 20px #ff00cc,0 0 40px #00f7ff,0 0 60px #ff00cc,0 0 80px #00ff00; }
            }
            .grid{ display:flex; flex-wrap:wrap; justify-content:center; gap:30px; padding:20px; }
            .card{
                position:relative; width:280px; border-radius:15px; overflow:hidden; cursor:pointer;
                transition: transform 0.4s, box-shadow 0.4s; box-shadow:0 0 20px rgba(0,255,255,0.3);
            }
            .card:hover{ transform: scale(1.07); box-shadow: 0 0 40px #ff00cc,0 0 80px #00f7ff; }
            .card img{ width:100%; height:230px; object-fit:cover; display:block; }
            .card h3{
                position:absolute; bottom:0; width:100%; text-align:center; padding:12px 0; font-size:22px; font-weight:800;
                color:#fff; background: linear-gradient(90deg, rgba(255,0,204,0.6), rgba(0,247,255,0.6));
                text-shadow:0 0 8px #ff00cc,0 0 12px #00f7ff; letter-spacing:1px; transition:0.3s;
            }
            .card:hover h3{ background: linear-gradient(90deg, rgba(255,0,204,0.8), rgba(0,247,255,0.8)); text-shadow:0 0 12px #ff00cc,0 0 20px #00f7ff,0 0 30px #ff00cc; }
            .avg-stars{text-align:center;color:gold;margin-bottom:10px;}
            .modal{display:none;position:fixed; inset:0; background:rgba(0,0,0,0.95); justify-content:center; align-items:center; z-index:1000;}
            .modal-content{background:#111;border:2px solid #00f7ff;border-radius:20px;width:90%; max-width:650px; max-height:85vh; overflow-y:auto; padding:20px; box-shadow:0 0 40px #ff00cc;}
            .modal-content img{width:100%; border-radius:10px; margin-bottom:15px;}
            .recipe{white-space: pre-line;color:#00f7ff; margin-top:10px;}
            .review{border-top:1px solid #333;padding:10px 0;font-size:0.9em;}
            .stars{color:gold;}
            .close{text-align:right;cursor:pointer;font-size:18px;color:#ff00cc;}
            .top-list{position:fixed;right:20px;bottom:20px;background:rgba(0,0,0,0.7);padding:15px 20px;border-radius:12px;border:2px solid #00f7ff;max-width:220px; z-index:500; box-shadow:0 0 20px #00f7ff55;}
            .top-list h3{margin:0 0 10px 0;text-align:center;text-transform:uppercase;color:#ff00cc;font-size:18px;text-shadow:0 0 6px #ff00cc,0 0 12px #00f7ff;}
            .top-list ul{list-style:none;padding:0;margin:0;}
            .top-list li{padding:6px 0;font-weight:600;color:#fff;border-bottom:1px solid rgba(255,255,255,0.1);}
        </style>
        <script>
            let clickCount=0;
            function openModal(name,img,recipe,reviewsHTML){
                document.getElementById("modal-title").innerText=name;
                document.getElementById("modal-img").src=img;
                document.getElementById("modal-recipe").innerText=recipe;
                document.getElementById("modal-reviews").innerHTML=reviewsHTML;
                document.getElementById("modal").style.display="flex";
            }
            function closeModal(){ document.getElementById("modal").style.display="none"; }
            document.getElementById("main-title")?.addEventListener("click",()=>{
                clickCount++;
                if(clickCount===5){
                    openModal(
                        "Secret Elixir",
                        "https://images.unsplash.com/photo-1603034280647-5f97118a0086?fit=crop&w=600&q=80",
                        "- 50ml gin\\n- 20ml limetková šťava\\n- 15ml jednoduchý sirup\\n- štipka tajného prášku",
                        "<div class='review'><strong>Neznámy</strong>: Tajomný a luxusný! ★★★★★</div>"
                    );
                    clickCount=0;
                }
            });
        </script>
    </head>
    <body>
        <h1 id="main-title">Luxusné Koktaily</h1>
        <div class="grid">
        {% for drink in cocktails %}
            <div class="card" onclick="openModal(
                `{{ drink.luxury_name }}`,
                `{{ drink.image }}`,
                `{{ drink.recipe }}`,
                `{% for review in drink.reviews %}
                    <div class='review'>
                        <div class='stars'>
                        {% for i in range(5) %}
                            {% if i < review.rating %}★{% else %}☆{% endif %}
                        {% endfor %}
                        </div>
                        <strong>{{ review.name }}</strong><br>{{ review.text }}
                    </div>
                {% endfor %}`
            )">
                <div class="avg-stars">
                    {% for i in range(5) %}
                        {% if i < drink.avg_rating %}★{% else %}☆{% endif %}
                    {% endfor %}
                </div>
                <img src="{{ drink.image }}">
                <h3>{{ drink.luxury_name }}</h3>
            </div>
        {% endfor %}
        </div>

        <div class="top-list">
            <h3>Top Drinky</h3>
            <ul>
                {% for drink in top_drinks %}
                    <li>{{ drink.luxury_name }} ({{ drink.avg_rating }}★)</li>
                {% endfor %}
            </ul>
        </div>

        <div id="modal" class="modal" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="close" onclick="closeModal()">Zatvoriť</div>
                <h2 id="modal-title"></h2>
                <img id="modal-img">
                <h3>Recept</h3>
                <div id="modal-recipe" class="recipe"></div>
                <h3>Recenzie</h3>
                <div id="modal-reviews"></div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, cocktails=cocktails, top_drinks=top_drinks)

if __name__ == "__main__":
    app.run(debug=True)