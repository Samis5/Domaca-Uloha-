from flask import Flask, render_template_string
import os
import random
import threading
import webbrowser

import requests

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
    {"name": "Kamil", "text": "Skvelé farby a chuť!", "rating": 5},
]

luxury_names = [
    "Sunset Royale",
    "Velvet Martini",
    "Golden Oasis",
    "Crystal Lagoon",
    "Midnight Bloom",
    "Starlight Mojito",
    "Aurora Spritz",
    "Moonlit Margarita",
    "Sapphire Collins",
    "Neon Nectar",
]

fallback_cocktails = [
    {
        "name": "Virgin Mojito",
        "image": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?fit=crop&w=800&q=80",
        "ingredients": [
            {"name": "Limetka", "measure": "1 ks"},
            {"name": "Mäta", "measure": "8 listov"},
            {"name": "Cukrový sirup", "measure": "20 ml"},
            {"name": "Sýtená voda", "measure": "120 ml"},
        ],
    },
    {
        "name": "Berry Splash",
        "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?fit=crop&w=800&q=80",
        "ingredients": [
            {"name": "Lesné ovocie", "measure": "60 g"},
            {"name": "Tonic", "measure": "150 ml"},
            {"name": "Ľad", "measure": "podľa chuti"},
        ],
    },
]


def build_recipe(ingredients):
    if not ingredients:
        return "Recept momentálne nie je dostupný."

    return "\n".join(
        f"- {item.get('name', '')} ({item.get('measure', '')})" for item in ingredients[:6]
    )


def enrich_cocktails(cocktails):
    for i, drink in enumerate(cocktails):
        drink["luxury_name"] = luxury_names[i % len(luxury_names)]
        drink["reviews"] = random.sample(reviews_list, 4)
        drink["avg_rating"] = round(
            sum(r["rating"] for r in drink["reviews"]) / len(drink["reviews"])
        )
        drink["recipe"] = build_recipe(drink.get("ingredients", []))

    return cocktails


def load_cocktails():
    try:
        response = requests.get("https://boozeapi.com/api/v1/cocktails", timeout=5)
        response.raise_for_status()
        raw = response.json()
        cocktails = raw.get("data", [])
        source = "API"
    except Exception:
        cocktails = fallback_cocktails.copy()
        source = "Lokálne dáta"

    return enrich_cocktails(cocktails), source


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/")
def home():
    cocktails, data_source = load_cocktails()
    top_drinks = sorted(cocktails, key=lambda x: x["avg_rating"], reverse=True)[:5]
    avg_all = round(sum(d["avg_rating"] for d in cocktails) / len(cocktails), 1) if cocktails else 0

    html_template = """
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Luxusné Koktaily</title>
        <style>
            :root{--bg1:#0a0a1f;--bg2:#18183b;--accent:#00f7ff;--pink:#ff00cc;}
            *{box-sizing:border-box}
            body {margin:0;font-family:'Segoe UI',sans-serif;background:linear-gradient(120deg,var(--bg1),var(--bg2));color:#fff;}
            .container{max-width:1200px;margin:0 auto;padding:20px;}
            h1{text-align:center;font-size:clamp(36px,8vw,76px);margin:25px 0;text-transform:uppercase;letter-spacing:2px;text-shadow:0 0 15px var(--pink),0 0 25px var(--accent);}
            .sub{display:flex;justify-content:center;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:18px;}
            .badge{padding:6px 12px;border-radius:999px;background:#ffffff10;border:1px solid #ffffff33;font-size:13px}
            .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px;}
            .stat{background:#ffffff0d;border:1px solid #ffffff22;border-radius:12px;padding:12px;}
            .stat strong{display:block;color:var(--accent);font-size:22px}
            .controls{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin:18px 0 24px;}
            .controls input,.controls select,.controls button{border:none;border-radius:10px;padding:10px 12px;font-size:14px}
            .controls input,.controls select{min-width:220px;background:#ffffffee}
            .controls button{background:linear-gradient(90deg,var(--pink),var(--accent));color:#fff;font-weight:700;cursor:pointer}
            .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;}
            .card{position:relative;border-radius:14px;overflow:hidden;cursor:pointer;background:#0f1030;box-shadow:0 0 22px rgba(0,247,255,.2);transition:.25s transform,.25s box-shadow}
            .card:hover{transform:translateY(-4px) scale(1.01);box-shadow:0 0 24px rgba(255,0,204,.55)}
            .card img{width:100%;height:220px;object-fit:cover;display:block}
            .card .content{padding:10px 12px 14px}
            .card h3{margin:0 0 8px 0}
            .avg-stars{color:gold;font-size:18px;margin-bottom:6px}
            .muted{opacity:.8;font-size:13px}
            .top-list{margin:26px 0 12px;background:#00000055;padding:14px;border-radius:12px;border:1px solid #ffffff22}
            .top-list h3{margin-top:0;color:var(--pink)}
            .top-list ul{margin:0;padding-left:18px}
            .modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.9);justify-content:center;align-items:center;z-index:1000;padding:15px}
            .modal-content{background:#111;border:2px solid var(--accent);border-radius:20px;width:min(700px,100%);max-height:90vh;overflow-y:auto;padding:20px;box-shadow:0 0 40px #ff00cc66}
            .modal-content img{width:100%;border-radius:10px;margin-bottom:15px}
            .recipe{white-space:pre-line;color:var(--accent)}
            .review{border-top:1px solid #333;padding:10px 0;font-size:.95em}
            .stars{color:gold}
            .close{text-align:right;cursor:pointer;font-size:18px;color:var(--pink)}
            .empty{display:none;text-align:center;opacity:.85;margin:18px 0}
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

            function filterCards(){
                const query = document.getElementById('searchInput').value.toLowerCase().trim();
                const minRating = Number(document.getElementById('ratingFilter').value || 0);
                const cards = [...document.querySelectorAll('.card')];
                let visible = 0;
                cards.forEach((card) => {
                    const name = card.dataset.name.toLowerCase();
                    const rating = Number(card.dataset.rating);
                    const show = name.includes(query) && rating >= minRating;
                    card.style.display = show ? 'block' : 'none';
                    if(show) visible += 1;
                });
                document.getElementById('emptyState').style.display = visible ? 'none' : 'block';
            }

            function openRandomDrink(){
                const cards = [...document.querySelectorAll('.card')].filter(c => c.style.display !== 'none');
                if(!cards.length) return;
                cards[Math.floor(Math.random()*cards.length)].click();
            }

            window.addEventListener("DOMContentLoaded", () => {
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

                document.getElementById('searchInput').addEventListener('input', filterCards);
                document.getElementById('ratingFilter').addEventListener('change', filterCards);
                document.getElementById('randomDrinkBtn').addEventListener('click', openRandomDrink);

                document.addEventListener("keydown", (event) => {
                    if (event.key === "Escape") closeModal();
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <h1 id="main-title">Luxusné Koktaily</h1>
            <div class="sub">
                <span class="badge">Zdroj dát: {{ data_source }}</span>
                <span class="badge">Klikni 5x na nadpis pre easter egg 😎</span>
            </div>

            <div class="stats">
                <div class="stat"><span>Počet drinkov</span><strong>{{ cocktails|length }}</strong></div>
                <div class="stat"><span>Priemerné hodnotenie</span><strong>{{ avg_all }}★</strong></div>
                <div class="stat"><span>TOP drink</span><strong>{{ top_drinks[0].luxury_name if top_drinks else '-' }}</strong></div>
            </div>

            <div class="controls">
                <input id="searchInput" type="text" placeholder="Hľadaj drink podľa názvu...">
                <select id="ratingFilter">
                    <option value="0">Všetky hodnotenia</option>
                    <option value="3">3★ a viac</option>
                    <option value="4">4★ a viac</option>
                    <option value="5">Iba 5★</option>
                </select>
                <button id="randomDrinkBtn" type="button">Náhodný drink</button>
            </div>

            <div class="grid">
            {% for drink in cocktails %}
                <div class="card" data-name="{{ drink.luxury_name }}" data-rating="{{ drink.avg_rating }}" onclick="openModal(
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
                    <img src="{{ drink.image }}" alt="{{ drink.luxury_name }}" loading="lazy">
                    <div class="content">
                        <div class="avg-stars">
                            {% for i in range(5) %}
                                {% if i < drink.avg_rating %}★{% else %}☆{% endif %}
                            {% endfor %}
                        </div>
                        <h3>{{ drink.luxury_name }}</h3>
                        <div class="muted">Klikni pre recept a recenzie</div>
                    </div>
                </div>
            {% endfor %}
            </div>
            <div class="empty" id="emptyState">Nenašli sa žiadne drinky pre tento filter.</div>

            <div class="top-list">
                <h3>Top Drinky</h3>
                <ul>
                    {% for drink in top_drinks %}
                        <li>{{ drink.luxury_name }} ({{ drink.avg_rating }}★)</li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <div id="modal" class="modal" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="close" onclick="closeModal()">Zatvoriť</div>
                <h2 id="modal-title"></h2>
                <img id="modal-img" alt="Drink detail">
                <h3>Recept</h3>
                <div id="modal-recipe" class="recipe"></div>
                <h3>Recenzie</h3>
                <div id="modal-reviews"></div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        cocktails=cocktails,
        top_drinks=top_drinks,
        avg_all=avg_all,
        data_source=data_source,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app_url = f"http://127.0.0.1:{port}"
    threading.Timer(1, lambda: webbrowser.open(app_url)).start()
    app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)
