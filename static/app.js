// Ждем, пока вся страница (HTML) загрузится
document.addEventListener("DOMContentLoaded", () => {
    loadMenu();
});

async function loadMenu() {
    // В ваших SQL-тестах вы добавляли блюда в филиал с ID = 1
    const branchId = 1; 
    const menuContainer = document.getElementById('menu-container');

    try {
        // Делаем фоновый запрос к нашему Python-бэкенду
        const response = await fetch(`/api/menu/${branchId}`);
        
        if (!response.ok) {
            throw new Error("Ошибка при получении данных с сервера");
        }

        // Преобразуем ответ от сервера в массив JavaScript-объектов
        const menuItems = await response.json();

        // Очищаем надпись "Загрузка меню..."
        menuContainer.innerHTML = '';

        if (menuItems.length === 0) {
            menuContainer.innerHTML = '<p style="text-align: center; grid-column: 1 / -1;">Меню пока пустое.</p>';
            return;
        }

        // Проходимся по каждому блюду из БД и создаем для него карточку (без картинки)
        menuItems.forEach(item => {
            const description = item.description ? item.description : 'Традиционное блюдо';
            
            // Формируем HTML-карточку
            const itemHTML = `
                <div class="menu-item">
                    <div class="item-info">
                        <h3>${item.item_name}</h3>
                        <p>${description}</p>
                        <div class="price">${item.price} ₽</div>
                    </div>
                </div>
            `;
            
            // Добавляем карточку на страницу
            menuContainer.innerHTML += itemHTML;
        });

    } catch (error) {
        console.error("Ошибка:", error);
        menuContainer.innerHTML = '<p style="text-align: center; grid-column: 1 / -1; color: red;">Не удалось загрузить меню. Проверьте подключение к базе данных.</p>';
    }
}
