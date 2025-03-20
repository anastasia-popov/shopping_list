async function fetchShoppingList() {
    const response = await fetch('/api/shopping-list');
    const data = await response.json();
    renderShoppingList(data);
}

function renderShoppingList(items) {
    const shoppingListContainer = document.getElementById('shopping-list');
    const boughtListContainer = document.getElementById('bought-list');
    shoppingListContainer.innerHTML = '';
    boughtListContainer.innerHTML = '';
    
    const aisles = {};
    items.forEach(item => {
        if (!item.is_bought) {
            if (!aisles[item.aisle]) aisles[item.aisle] = [];
            aisles[item.aisle].push(item);
        } else {
            const itemElement = createItemElement(item, true);
            boughtListContainer.appendChild(itemElement);
        }
    });
    
    for (const aisle in aisles) {
        const section = document.createElement('div');
        section.classList.add('aisle');
        section.innerHTML = `<h3>${aisle}</h3>`;
        aisles[aisle].forEach(item => {
            const itemElement = createItemElement(item, false);
            section.appendChild(itemElement);
        });
        shoppingListContainer.appendChild(section);
    }
}

function createItemElement(item, isBought) {
    const div = document.createElement('div');
    div.classList.add('item');
    if (isBought) div.classList.add('bought');
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = isBought;
    checkbox.addEventListener('change', () => markAsBought(item));
    
    div.appendChild(checkbox);
    div.appendChild(document.createTextNode(`${item.item} (${item.amount})`));
    return div;
}

async function markAsBought(item) {
    await fetch(`/api/shopping-list/${item.item}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_bought: true })
    });
    fetchShoppingList();
}

fetchShoppingList();

