// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initializeMessages();
    initializeTableSearch();
    initializeButtons();
    initializeDatePickers();
    checkOverdue();
});

// Gestion des messages flash améliorée
function initializeMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        // Ajout d'un bouton de fermeture
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.className = 'message-close';
        closeBtn.onclick = () => fadeOutAndRemove(msg);
        msg.appendChild(closeBtn);

        // Animation d'entrée
        msg.style.opacity = '1';
        msg.style.transform = 'translateY(0)';

        // Auto-suppression après délai
        setTimeout(() => fadeOutAndRemove(msg), 5000);
    });
}

function fadeOutAndRemove(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(-10px)';
    setTimeout(() => element.remove(), 300);
}

// Recherche en temps réel améliorée
function initializeTableSearch() {
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        const tableId = input.dataset.search;
        let debounceTimer;

        input.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                filterTable(input.id, tableId);
            }, 300);
        });
    });
}

function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    let hasResults = false;

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            if (cell) {
                const text = cell.textContent || cell.innerText;
                if (text.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    hasResults = true;
                    break;
                }
            }
        }
        
        if (found) {
            rows[i].style.display = '';
            rows[i].style.animation = 'fadeIn 0.5s ease forwards';
        } else {
            rows[i].style.display = 'none';
        }
    }

    // Afficher un message si aucun résultat
    const noResults = table.querySelector('.no-results');
    if (!hasResults && filter !== '') {
        if (!noResults) {
            const tr = document.createElement('tr');
            tr.className = 'no-results';
            tr.innerHTML = `<td colspan="100%" style="text-align: center; padding: 1rem;">Aucun résultat trouvé pour "${filter}"</td>`;
            table.querySelector('tbody').appendChild(tr);
        }
    } else if (noResults) {
        noResults.remove();
    }
}

// Animation des boutons améliorée
function initializeButtons() {
    document.querySelectorAll('button, .button').forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Confirmation personnalisée
async function confirmAction(message) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Confirmation</h2>
                <p>${message}</p>
                <div class="modal-buttons">
                    <button class="button button-secondary" data-action="cancel">Annuler</button>
                    <button class="button button-primary" data-action="confirm">Confirmer</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeAndResolve(false);
            }
        });

        modal.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', () => {
                closeAndResolve(button.dataset.action === 'confirm');
            });
        });

        function closeAndResolve(value) {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
            resolve(value);
        }
    });
}

// Gestion améliorée des dates
function initializeDatePickers() {
    const loanDate = document.getElementById('loan_date');
    const dueDate = document.getElementById('due_date');

    if (loanDate && dueDate) {
        loanDate.addEventListener('change', updateDueDate);
        // Initialiser avec la date du jour
        if (!loanDate.value) {
            loanDate.valueAsDate = new Date();
            updateDueDate();
        }
    }
}

function updateDueDate() {
    const loanDate = document.getElementById('loan_date');
    const dueDate = document.getElementById('due_date');
    if (loanDate && dueDate) {
        const date = new Date(loanDate.value);
        date.setDate(date.getDate() + 14);
        dueDate.value = date.toISOString().split('T')[0];
    }
}

// Vérification des retards améliorée
function checkOverdue() {
    const today = new Date();
    document.querySelectorAll('.loan-row').forEach(row => {
        const dueDate = new Date(row.dataset.dueDate);
        if (today > dueDate && row.dataset.status === 'active') {
            row.classList.add('overdue');
            const dueDateCell = row.querySelector('.due-date');
            if (dueDateCell) {
                dueDateCell.title = 'En retard';
            }
        }
    });
}
