document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector(".subscription-table");

    if (!table) {
        return;
    }

    const headers = table.querySelectorAll("thead th");
    const tbody = table.querySelector("tbody");

    const sortableColumns = {
        0: "text",      // Service
        1: "number",    // Price
        2: "text",      // Category
        3: "text",      // Billing cycle
        4: "date",      // Started on
        5: "date",      // Next payment
        7: "date",      // Created at
        8: "date",      // Updated at
        9: "text"       // Auto Renew
    };

    headers.forEach((header, columnIndex) => {
        if (!(columnIndex in sortableColumns)) {
            return;
        }

        header.classList.add("sortable");
        header.style.cursor = "pointer";

        const arrow = document.createElement("span");
        arrow.classList.add("sort-arrow");
        arrow.textContent = " ↕";
        header.appendChild(arrow);

        header.addEventListener("click", () => {
            const type = sortableColumns[columnIndex];
            const currentDirection = header.dataset.direction || "none";

            const direction = currentDirection === "asc" ? "desc" : "asc";

            headers.forEach((otherHeader) => {
                if (otherHeader !== header) {
                    delete otherHeader.dataset.direction;

                    const otherArrow = otherHeader.querySelector(".sort-arrow");

                    if (otherArrow) {
                        otherArrow.textContent = " ↕";
                    }
                }
            });

            header.dataset.direction = direction;
            arrow.textContent = direction === "asc" ? " ↑" : " ↓";

            const rows = Array.from(tbody.querySelectorAll("tr"));

            rows.sort((rowA, rowB) => {
                const cellA = rowA.children[columnIndex].textContent.trim();
                const cellB = rowB.children[columnIndex].textContent.trim();

                let comparison = 0;

                if (type === "number") {
                    const numberA = parseFloat(cellA.replace(",", "."));
                    const numberB = parseFloat(cellB.replace(",", "."));

                    comparison = numberA - numberB;
                }

                if (type === "text") {
                    comparison = cellA.localeCompare(cellB);
                }

                if (type === "date") {
                    const [dayA, monthA, yearA] = cellA.split(".");
                    const [dayB, monthB, yearB] = cellB.split(".");

                    const dateA = new Date(yearA, monthA - 1, dayA);
                    const dateB = new Date(yearB, monthB - 1, dayB);

                    comparison = dateA - dateB;
                }

                return direction === "asc" ? comparison : -comparison;
            });

            rows.forEach((row) => tbody.appendChild(row));
        });
    });
});