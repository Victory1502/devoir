// Configuration de l'API
const API_URL = 'http://localhost:8000/personnages';
const TOKEN = 'mon_super_token_secret';

// Fonction pour récupérer les personnages
async function getPersonnages() {
    try {
        // Élément où afficher les résultats ou les erreurs
        const resultElement = document.getElementById('result');
        resultElement.innerHTML = 'Chargement...';
        
        // Configuration de la requête avec le token d'authentification
        const options = {
            method: 'GET',
            headers: {
                'token': TOKEN
            }
        };
        
        // Envoi de la requête
        const response = await fetch(API_URL, options);
        
        // Vérification du statut de la réponse
        if (!response.ok) {
            // Si le statut est 401, c'est une erreur d'authentification
            if (response.status === 401) {
                throw new Error('Erreur d\'authentification: Token invalide ou manquant');
            }
            // Pour les autres erreurs
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        // Conversion de la réponse en JSON
        const data = await response.json();
        
        // Affichage du résultat
        resultElement.innerHTML = '';
        
        // Création d'un titre pour indiquer le succès
        const title = document.createElement('h2');
        title.textContent = `${data.length} personnages récupérés`;
        resultElement.appendChild(title);
        
        // Parcours et affichage de chaque personnage
        data.forEach(personnage => {
            const card = document.createElement('div');
            card.className = 'card';
            
            // Création du contenu HTML pour chaque personnage
            card.innerHTML = `
                <h3>${personnage.nom}</h3>
                <p><strong>Profession:</strong> ${personnage.profession}</p>
                <p><strong>Âge:</strong> ${personnage.age} ans</p>
                <p><strong>Pouvoir:</strong> ${personnage.pouvoir || 'Aucun'}</p>
            `;
            
            resultElement.appendChild(card);
        });
        
    } catch (error) {
        // Gestion des erreurs
        const resultElement = document.getElementById('result');
        resultElement.innerHTML = `
            <div class="error">
                <h3>Erreur</h3>
                <p>${error.message}</p>
            </div>
        `;
        console.error('Erreur lors de la récupération des personnages:', error);
    }
}

// Exécution de la fonction lors du chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    // Recherche du bouton et ajout d'un écouteur d'événement
    const button = document.getElementById('loadButton');
    if (button) {
        button.addEventListener('click', getPersonnages);
    } else {
        // Si aucun bouton n'est trouvé, exécuter directement
        getPersonnages();
    }
});