let nodes = [];
let links = [];
let addingNode = false;
let addingEdge = false;
let deleteMode = false;
let selectedNode = null;
let sourceNode = null;

const width = window.innerWidth - 320;
const height = window.innerHeight - 20;

const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(150))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

function updateGraph() {
    const link = svg.selectAll(".link")
        .data(links)
        .join("g")
        .attr("class", "link");

    link.selectAll("line")
        .data(d => [d])
        .join("line")
        .attr("stroke", "#999")
        .attr("stroke-width", 2)
        .attr("marker-end", "url(#arrowhead)");

    link.selectAll("text")
        .data(d => [d])
        .join("text")
        .attr("class", "link-label")
        .attr("dx", 50)
        .attr("dy", -5)
        .text(d => `Time: ${d.time}min, Cost: $${d.cost}`);

    const node = svg.selectAll(".node")
        .data(nodes)
        .join("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    node.selectAll("circle")
        .data(d => [d])
        .join("circle")
        .attr("r", 20)
        .attr("class", d => d.type)
        .on("click", handleNodeClick);

    node.selectAll("text")
        .data(d => [d])
        .join("text")
        .attr("dx", 25)
        .attr("dy", 5)
        .text(d => d.name);

    simulation.nodes(nodes)
        .on("tick", ticked);

    simulation.force("link").links(links);
    simulation.alpha(1).restart();
}

function ticked() {
    svg.selectAll(".link line")
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    svg.selectAll(".link text")
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);

    svg.selectAll(".node")
        .attr("transform", d => `translate(${d.x},${d.y})`);
}

function createEmptyGraph() {
    nodes = [];
    links = [];
    updateGraph();
    updateNodeSelects();
}

function loadGraphFromFile(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const data = JSON.parse(e.target.result);
        nodes = data.nodes;
        links = data.links;
        updateGraph();
        updateNodeSelects();
    };
    reader.readAsText(file);
}

function toggleNodeType() {
    addingNode = !addingNode;
    addingEdge = false;
    deleteMode = false;
}

function toggleAddEdge() {
    addingEdge = !addingEdge;
    addingNode = false;
    deleteMode = false;
    sourceNode = null;
}

function toggleDeleteMode() {
    deleteMode = !deleteMode;
    addingNode = false;
    addingEdge = false;
    sourceNode = null;
}

function handleNodeClick(event, d) {
    if (addingEdge) {
        if (!sourceNode) {
            sourceNode = d;
        } else {
            const time = prompt("Enter delivery time (minutes):");
            const cost = prompt("Enter delivery cost ($):");
            if (time && cost) {
                links.push({
                    source: sourceNode.id,
                    target: d.id,
                    time: parseInt(time),
                    cost: parseInt(cost)
                });
                updateGraph();
            }
            sourceNode = null;
        }
    } else if (deleteMode) {
        nodes = nodes.filter(n => n.id !== d.id);
        links = links.filter(l => l.source.id !== d.id && l.target.id !== d.id);
        updateGraph();
        updateNodeSelects();
    }
}

function updateNodeSelects() {
    const startSelect = document.getElementById("startNode");
    const endSelect = document.getElementById("endNode");
    startSelect.innerHTML = "";
    endSelect.innerHTML = "";
    
    nodes.forEach(node => {
        const option1 = document.createElement("option");
        const option2 = document.createElement("option");
        option1.value = option2.value = node.id;
        option1.text = option2.text = node.name;
        startSelect.appendChild(option1);
        endSelect.appendChild(option2);
    });
}

function findShortestPath() {
    const startId = document.getElementById("startNode").value;
    const endId = document.getElementById("endNode").value;
    const optimizationType = document.getElementById("optimizationType").value;
    
    const distances = {};
    const previous = {};
    const unvisited = new Set();
    
    nodes.forEach(node => {
        distances[node.id] = Infinity;
        previous[node.id] = null;
        unvisited.add(node.id);
    });
    
    distances[startId] = 0;
    
    while (unvisited.size > 0) {
        let current = null;
        let minDistance = Infinity;
        
        for (const nodeId of unvisited) {
            if (distances[nodeId] < minDistance) {
                minDistance = distances[nodeId];
                current = nodeId;
            }
        }
        
        if (current === null) break;
        if (current === endId) break;
        
        unvisited.delete(current);
        
        const neighbors = links.filter(l => l.source.id === current);
        for (const link of neighbors) {
            const alt = distances[current] + getWeight(link, optimizationType);
            if (alt < distances[link.target.id]) {
                distances[link.target.id] = alt;
                previous[link.target.id] = current;
            }
        }
    }
    
    // Reconstruct path
    const path = [];
    let current = endId;
    while (current !== null) {
        path.unshift(current);
        current = previous[current];
    }
    
    displayPath(path, optimizationType);
}

function getWeight(link, optimizationType) {
    switch (optimizationType) {
        case 'time':
            return link.time;
        case 'cost':
            return link.cost;
        case 'both':
            return link.time + link.cost;
    }
}

function displayPath(path, optimizationType) {
    let totalTime = 0;
    let totalCost = 0;
    
    for (let i = 0; i < path.length - 1; i++) {
        const link = links.find(l => 
            l.source.id === path[i] && l.target.id === path[i + 1]
        );
        if (link) {
            totalTime += link.time;
            totalCost += link.cost;
        }
    }
    
    const pathNodes = path.map(id => 
        nodes.find(n => n.id === id).name
    ).join(" → ");
    
    document.getElementById("pathResult").innerHTML = 
        `Path: ${pathNodes}<br>` +
        `Total Time: ${totalTime} minutes<br>` +
        `Total Cost: $${totalCost}`;
}

function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}
