document.addEventListener('DOMContentLoaded', () => {
    fetch('./data.json')
        .then(response => response.json())
        .then(data => {
            // Update Title and Subtitle
            document.getElementById('edition-title').textContent = data.title;
            document.getElementById('edition-subtitle').textContent = data.subtitle;
            document.getElementById('edition-source').textContent = `Source: ${data.source_info["Source Name"]} (${data.source_info.Year})`;

            const container = document.getElementById('infographic-content');
            container.innerHTML = ''; // Clear existing content

            data.content_blocks.forEach(block => {
                if (block.type === 'metrics') {
                    const section = document.createElement('div');
                    section.className = 'grid grid-cols-1 md:grid-cols-2 gap-6';
                    section.innerHTML = `<h2 class="text-2xl font-bold col-span-full">${block.title}</h2>`;
                    
                    block.items.forEach(item => {
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'bg-slate-50 p-6 rounded-xl';
                        itemDiv.innerHTML = `
                            <div class="text-3xl font-bold text-[var(--brand-primary)]">${item.value}</div>
                            <div class="text-sm text-slate-600">${item.label}</div>
                        `;
                        section.appendChild(itemDiv);
                    });
                    container.appendChild(section);
                } else if (block.type === 'comparison') {
                    const section = document.createElement('div');
                    section.className = 'grid grid-cols-2 gap-4';
                    section.innerHTML = `
                        <h2 class="text-2xl font-bold col-span-full">${block.title}</h2>
                        <div class="font-bold text-center border-b pb-2">${block.side_a_name}</div>
                        <div class="font-bold text-center border-b pb-2">${block.side_b_name}</div>
                    `;
                    block.items.forEach(item => {
                        section.innerHTML += `<div class="p-2 text-sm">${item.a}</div><div class="p-2 text-sm">${item.b}</div>`;
                    });
                    container.appendChild(section);
                } else if (block.type === 'insights') {
                    const section = document.createElement('div');
                    section.className = 'bg-[var(--brand-light)] p-8 rounded-2xl';
                    section.innerHTML = `<h2 class="text-2xl font-bold mb-4">${block.title}</h2>`;
                    block.points.forEach(point => {
                        section.innerHTML += `<p class="mb-3 italic">• ${point}</p>`;
                    });
                    container.appendChild(section);
                }
            });
        })
        .catch(error => console.error('Error loading data:', error));
});
