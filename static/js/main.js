// Animations pour les messages flash
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        msg.style.opacity = '1';
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        }, 3000);
    });
});

// Recherche en temps réel dans les tableaux
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            if (cell) {
                const text = cell.textContent || cell.innerText;
                if (text.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        
        rows[i].style.display = found ? '' : 'none';
        if (found) {
            rows[i].classList.add('fade-in');
        }
    }
}

// Animation pour les boutons
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

// Confirmation personnalisée
function confirmAction(message) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Confirmation</h2>
            <p>${message}</p>
            <div class="modal-buttons">
                <button onclick="this.closest('.modal').remove(); return false;" class="button-secondary">Annuler</button>
                <button onclick="this.closest('.modal').setAttribute('data-result', 'true'); this.closest('.modal').remove();" class="button-primary">Confirmer</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    return new Promise(resolve => {
        const checkResult = setInterval(() => {
            if (!document.body.contains(modal)) {
                clearInterval(checkResult);
                resolve(modal.getAttribute('data-result') === 'true');
            }
        }, 100);
    });
}

// Gestion des dates d'emprunt
function updateDueDate() {
    const loanDate = document.getElementById('loan_date');
    const dueDate = document.getElementById('due_date');
    if (loanDate && dueDate) {
        const date = new Date(loanDate.value);
        date.setDate(date.getDate() + 14); // 14 jours par défaut
        dueDate.value = date.toISOString().split('T')[0];
    }
}

// Notification des retards
function checkOverdue() {
    const today = new Date();
    document.querySelectorAll('.loan-row').forEach(row => {
        const dueDate = new Date(row.dataset.dueDate);
        if (today > dueDate && row.dataset.status === 'active') {
            row.classList.add('overdue');
        }
    });
}
