document.addEventListener("DOMContentLoaded", () => {
  // --- STATE VARIABLES ---
  let activeSchema = null;
  let activeDb = "ecommerce";
  let availableDatabases = [];
  
  // Suggested questions mapped to databases
  const suggestions = {
    ecommerce: [
      "Show all customers",
      "List all products in Electronics category",
      "Show all orders with a total amount greater than 100",
      "Find the total amount of all orders",
      "Show customer orders with customer names",
      "How many orders were placed by each customer?"
    ],
    company: [
      "List all employees",
      "What is the average salary of employees in each department?",
      "Find the names of all employees who earn more than 100000",
      "Find projects with a budget greater than 100000",
      "Show employees and their projects"
    ],
    music: [
      "List all songs",
      "Find the top 5 most played songs and their artists",
      "Which country has the most artists?",
      "Show songs in Alternative genre"
    ],
    custom: [
      "SELECT name FROM sqlite_master WHERE type='table';"
    ]
  };

  // --- DOM ELEMENTS ---
  const dbSelector = document.getElementById("db-selector");
  const schemaSearch = document.getElementById("schema-search");
  const tableListContainer = document.getElementById("table-list-container");
  
  const nlpQueryInput = document.getElementById("nlp-query-input");
  const generateBtn = document.getElementById("generate-btn");
  const suggestionsContainer = document.getElementById("suggestions-container");
  
  const sqlEditor = document.getElementById("sql-editor");
  const runQueryBtn = document.getElementById("run-query-btn");
  
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");
  
  const tableResultsWrapper = document.getElementById("table-results-wrapper");
  const queryStatsBar = document.getElementById("query-stats-bar");
  const execTimeLabel = document.getElementById("exec-time");
  const rowCountLabel = document.getElementById("row-count");
  
  const explanationContainer = document.getElementById("explanation-container");
  const explanationText = document.getElementById("explanation-text");
  const erdContainerWrapper = document.getElementById("erd-container-wrapper");
  
  const llmBadge = document.getElementById("llm-badge");
  const heuristicBadge = document.getElementById("heuristic-badge");
  
  // Modals
  const settingsBtn = document.getElementById("settings-btn");
  const settingsModal = document.getElementById("settings-modal");
  const settingsClose = document.getElementById("settings-close");
  const settingsCancel = document.getElementById("settings-cancel");
  const settingsSave = document.getElementById("settings-save");
  const apiKeyInput = document.getElementById("api-key-input");
  
  const customDbBtn = document.getElementById("custom-db-btn");
  const customDbModal = document.getElementById("custom-db-modal");
  const customDbClose = document.getElementById("custom-db-close");
  const customDbCancel = document.getElementById("custom-db-cancel");
  const customDbSubmit = document.getElementById("custom-db-submit");
  const customSqlScript = document.getElementById("custom-sql-script");

  // --- LOCAL STORAGE KEY RETRIEVAL ---
  let geminiApiKey = localStorage.getItem("gemini_api_key") || "";
  if (apiKeyInput) {
    apiKeyInput.value = geminiApiKey;
  }
  updateBadgeStates();

  // --- INITIALIZE APP ---
  loadDatabaseList();

  // --- TAB NAVIGATION HANDLER ---
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      
      btn.classList.add("active");
      const activeTabId = btn.getAttribute("data-tab");
      document.getElementById(activeTabId).classList.add("active");
    });
  });

  // --- API CALLS ---
  
  // Fetch databases list from Flask
  async function loadDatabaseList() {
    try {
      const response = await fetch("/api/databases");
      const data = await response.json();
      
      availableDatabases = data.databases;
      activeDb = data.active;
      
      // Populate select option dropdown
      dbSelector.innerHTML = "";
      availableDatabases.forEach(db => {
        const option = document.createElement("option");
        option.value = db;
        // Capitalize for readability
        option.textContent = db.toUpperCase() + " DB";
        if (db === activeDb) option.selected = true;
        dbSelector.appendChild(option);
      });
      
      // Fetch schema details for active db
      fetchActiveSchema();
      renderSuggestionChips();
    } catch (err) {
      console.error("Error loading database lists:", err);
    }
  }

  // Fetch active schema metadata
  async function fetchActiveSchema() {
    try {
      tableListContainer.innerHTML = `<div class="spinner-container"><div class="spinner"></div></div>`;
      
      const response = await fetch("/api/schema");
      const data = await response.json();
      
      if (data.success) {
        activeSchema = data.schema;
        renderSchemaExplorer(activeSchema);
        renderERD(activeSchema);
      } else {
        tableListContainer.innerHTML = `<div class="empty-state"><p>Error fetching schema: ${data.error}</p></div>`;
      }
    } catch (err) {
      tableListContainer.innerHTML = `<div class="empty-state"><p>Server Connection Refused.</p></div>`;
    }
  }

  // Switch database
  dbSelector.addEventListener("change", async (e) => {
    const selectedDb = e.target.value;
    try {
      const response = await fetch("/api/select_db", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ db_key: selectedDb })
      });
      const data = await response.json();
      
      if (data.success) {
        activeDb = data.active;
        activeSchema = data.schema;
        renderSchemaExplorer(activeSchema);
        renderSuggestionChips();
        renderERD(activeSchema);
        clearResults();
      } else {
        alert("Failed to switch database: " + data.error);
      }
    } catch (err) {
      console.error(err);
    }
  });

  // --- RENDER SCHEMA EXPLORER (LEFT BAR) ---
  function renderSchemaExplorer(schema) {
    if (!schema || !schema.tables) return;
    tableListContainer.innerHTML = "";
    
    const filter = schemaSearch.value.toLowerCase();
    
    Object.keys(schema.tables).forEach(tableName => {
      const tableData = schema.tables[tableName];
      const cols = tableData.columns;
      
      // Check filtering match
      const nameMatch = tableName.toLowerCase().includes(filter);
      const colsMatch = cols.some(col => col.name.toLowerCase().includes(filter));
      
      if (filter && !nameMatch && !colsMatch) return; // Skip non-matching tables
      
      // Create table details card
      const card = document.createElement("div");
      card.className = "table-card";
      
      // Card Header
      const header = document.createElement("div");
      header.className = "table-card-header";
      header.innerHTML = `
        <span class="table-name">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16" style="color: var(--color-cyan);">
            <path d="M12 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h8zM4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H4z"/>
          </svg>
          ${tableName}
        </span>
        <span class="table-badge">${tableData.row_count} rows</span>
      `;
      card.appendChild(header);
      
      // Columns Container
      const colsContainer = document.createElement("div");
      colsContainer.className = "table-columns";
      
      cols.forEach(col => {
        const colRow = document.createElement("div");
        colRow.className = "column-row";
        
        let keyBadgeHtml = "";
        if (col.pk) {
          keyBadgeHtml = `<span class="key-badge key-pk" title="Primary Key">PK</span>`;
        } else if (col.fk) {
          keyBadgeHtml = `<span class="key-badge key-fk" title="Foreign Key referencing ${col.fk.table}(${col.fk.to})">FK</span>`;
        }
        
        colRow.innerHTML = `
          <span class="column-name">
            ${keyBadgeHtml}
            ${col.name}
          </span>
          <span class="column-type">${col.type}</span>
        `;
        colsContainer.appendChild(colRow);
      });
      card.appendChild(colsContainer);
      tableListContainer.appendChild(card);
      
      // Toggle Columns collapse/expand behavior
      header.addEventListener("click", () => {
        const isCollapsed = colsContainer.style.display === "none";
        colsContainer.style.display = isCollapsed ? "flex" : "none";
      });
    });
  }
  
  // Real-time schema search input binding
  schemaSearch.addEventListener("input", () => {
    if (activeSchema) renderSchemaExplorer(activeSchema);
  });

  // --- SUGGESTIONS CHIPS RENDER ---
  function renderSuggestionChips() {
    suggestionsContainer.innerHTML = `<span class="suggestion-label">Suggestions:</span>`;
    const list = suggestions[activeDb] || [];
    
    list.forEach(phrase => {
      const chip = document.createElement("button");
      chip.className = "suggestion-chip";
      chip.textContent = phrase;
      chip.addEventListener("click", () => {
        nlpQueryInput.value = phrase;
        // Trigger translation
        generateSql(phrase);
      });
      suggestionsContainer.appendChild(chip);
    });
  }

  // --- TRANSLATE NL TO SQL ---
  generateBtn.addEventListener("click", () => {
    const text = nlpQueryInput.value.trim();
    if (text) generateSql(text);
  });
  
  // Execute translation via backend
  async function generateSql(nlpQuestion) {
    try {
      setLoadingState(true);
      const response = await fetch("/api/generate_sql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: nlpQuestion,
          api_key: geminiApiKey
        })
      });
      const data = await response.json();
      
      if (data.success) {
        sqlEditor.value = data.sql;
        renderExplanation(data.explanation);
        
        // Auto run query
        executeActiveQuery(data.sql);
      } else {
        alert("Error generating query: " + data.error);
        setLoadingState(false);
      }
    } catch (err) {
      alert("Failed connecting to SQL generator.");
      setLoadingState(false);
    }
  }

  // --- EXECUTE SQL QUERY ---
  runQueryBtn.addEventListener("click", () => {
    const query = sqlEditor.value.trim();
    if (query) executeActiveQuery(query);
  });
  
  async function executeActiveQuery(querySql) {
    const startTime = performance.now();
    try {
      tableResultsWrapper.innerHTML = `<div class="spinner-container"><div class="spinner"></div><p style="font-size:0.85rem;color:var(--text-muted);">Executing query...</p></div>`;
      
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: querySql })
      });
      const data = await response.json();
      
      const endTime = performance.now();
      const timeTaken = Math.round(endTime - startTime);
      
      if (data.success) {
        if (data.type === "write") {
          // Render success message for writes (INSERT/UPDATE/DELETE/CREATE)
          tableResultsWrapper.innerHTML = `
            <div class="empty-state" style="color: var(--color-emerald);">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p>${data.message}</p>
            </div>
          `;
          queryStatsBar.style.display = "flex";
          execTimeLabel.textContent = `${timeTaken} ms`;
          rowCountLabel.textContent = `${data.rows_affected} rows affected`;
          
          // Re-fetch schema since data/structure changed
          fetchActiveSchema();
        } else {
          // Render data table for SELECT queries
          renderResultsTable(data.columns, data.rows);
          queryStatsBar.style.display = "flex";
          execTimeLabel.textContent = `${timeTaken} ms`;
          rowCountLabel.textContent = data.total_rows;
        }
        
        // Ensure Results tab is highlighted
        switchTab("results-tab");
      } else {
        // Render error message
        tableResultsWrapper.innerHTML = `
          <div class="empty-state" style="color: var(--color-rose);">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p>SQLite Execution Error: <code style="display:block;margin-top:0.5rem;font-family:var(--font-mono);font-size:0.8rem;background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:4px;">${data.error}</code></p>
          </div>
        `;
        queryStatsBar.style.display = "none";
      }
    } catch (err) {
      tableResultsWrapper.innerHTML = `<div class="empty-state"><p>Connection timeout/error.</p></div>`;
    } finally {
      setLoadingState(false);
    }
  }

  // --- RENDER DYNAMIC DATA TABLE ---
  function renderResultsTable(columns, rows) {
    if (!columns || columns.length === 0) {
      tableResultsWrapper.innerHTML = `
        <div class="empty-state">
          <p>No columns returned from the active result set.</p>
        </div>
      `;
      return;
    }
    
    if (!rows || rows.length === 0) {
      tableResultsWrapper.innerHTML = `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 012.008 1.24l.885 1.77a2.25 2.25 0 002.007 1.24h1.98a2.25 2.25 0 002.007-1.24l.885-1.77a2.25 2.25 0 012.007-1.24h3.86m-18 0h18"/>
          </svg>
          <p>Query ran successfully, but returned 0 rows.</p>
        </div>
      `;
      return;
    }
    
    // Construct HTML string
    let html = `<table class="output-table"><thead><tr>`;
    columns.forEach(col => {
      html += `<th>${col}</th>`;
    });
    html += `</tr></thead><tbody>`;
    
    rows.forEach(row => {
      html += `<tr>`;
      columns.forEach(col => {
        let val = row[col];
        if (val === null) val = `<span style="color:var(--text-dark);font-style:italic;">NULL</span>`;
        html += `<td>${val}</td>`;
      });
      html += `</tr>`;
    });
    html += `</tbody></table>`;
    
    tableResultsWrapper.innerHTML = html;
  }

  // --- RENDER EXPLANATION TAB ---
  function renderExplanation(text) {
    // Convert newlines to breaks or bullet lists for simple markdown-like display
    const formattedText = text
      .split("\n")
      .map(line => {
        if (line.trim().startsWith("-") || line.trim().startsWith("*")) {
          return `<li>${line.trim().substring(1).trim()}</li>`;
        }
        if (line.trim().match(/^\d+\./)) {
          return `<li><strong>${line.trim()}</strong></li>`;
        }
        return `<p style="margin-bottom:0.5rem;">${line}</p>`;
      })
      .join("");
      
    explanationContainer.innerHTML = `
      <h3>SQL Query Interpretation</h3>
      <ul class="explanation-steps" style="padding-left: 1.2rem; margin-top: 0.5rem;">
        ${formattedText}
      </ul>
    `;
  }

  // --- RENDER ERD VISUAL CONNECTIONS ---
  function renderERD(schema) {
    erdContainerWrapper.innerHTML = "";
    if (!schema || !schema.tables) {
      erdContainerWrapper.innerHTML = `<div class="empty-state"><p>No visual schema loaded.</p></div>`;
      return;
    }
    
    Object.keys(schema.tables).forEach(tableName => {
      const tableInfo = schema.tables[tableName];
      const node = document.createElement("div");
      node.className = "erd-node";
      
      let nodeHtml = `<div class="erd-node-title">${tableName}</div><div class="erd-node-columns">`;
      tableInfo.columns.forEach(col => {
        let cls = "";
        let keyChar = "";
        if (col.pk) {
          cls = "pk";
          keyChar = "🔑";
        } else if (col.fk) {
          cls = "fk";
          keyChar = "🔗";
        }
        nodeHtml += `<div class="erd-node-column ${cls}">
          <span>${keyChar} ${col.name}</span>
          <span>${col.type}</span>
        </div>`;
      });
      nodeHtml += `</div>`;
      node.innerHTML = nodeHtml;
      
      erdContainerWrapper.appendChild(node);
    });
  }

  // --- SETTINGS (API KEY) MODAL ---
  settingsBtn.addEventListener("click", () => {
    apiKeyInput.value = geminiApiKey;
    settingsModal.classList.add("open");
  });
  
  const closeSettings = () => settingsModal.classList.remove("open");
  settingsClose.addEventListener("click", closeSettings);
  settingsCancel.addEventListener("click", closeSettings);
  
  settingsSave.addEventListener("click", () => {
    geminiApiKey = apiKeyInput.value.trim();
    if (geminiApiKey) {
      localStorage.setItem("gemini_api_key", geminiApiKey);
    } else {
      localStorage.removeItem("gemini_api_key");
    }
    updateBadgeStates();
    closeSettings();
  });
  
  function updateBadgeStates() {
    if (geminiApiKey) {
      llmBadge.style.display = "inline-block";
      heuristicBadge.style.display = "none";
    } else {
      llmBadge.style.display = "none";
      heuristicBadge.style.display = "inline-block";
    }
  }

  // --- CUSTOM DATABASE MODAL ---
  customDbBtn.addEventListener("click", () => {
    customDbModal.classList.add("open");
  });
  
  const closeCustomDb = () => customDbModal.classList.remove("open");
  customDbClose.addEventListener("click", closeCustomDb);
  customDbCancel.addEventListener("click", closeCustomDb);
  
  customDbSubmit.addEventListener("click", async () => {
    const scriptText = customSqlScript.value.trim();
    if (!scriptText) {
      alert("Please enter a valid SQL script.");
      return;
    }
    
    try {
      customDbSubmit.disabled = true;
      customDbSubmit.textContent = "Creating...";
      
      const response = await fetch("/api/custom_db", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sql_script: scriptText })
      });
      const data = await response.json();
      
      if (data.success) {
        closeCustomDb();
        // Load active database info
        loadDatabaseList();
        clearResults();
        alert(data.message);
      } else {
        alert("Failed initializing custom database: " + data.error);
      }
    } catch (err) {
      alert("Error communicating with server.");
    } finally {
      customDbSubmit.disabled = false;
      customDbSubmit.textContent = "Create Database";
    }
  });

  // --- HELPER UTILITIES ---
  function setLoadingState(isLoading) {
    if (isLoading) {
      generateBtn.disabled = true;
      generateBtn.style.opacity = "0.5";
    } else {
      generateBtn.disabled = false;
      generateBtn.style.opacity = "1";
    }
  }
  
  function clearResults() {
    sqlEditor.value = "";
    nlpQueryInput.value = "";
    tableResultsWrapper.innerHTML = `
      <div class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <p>Run a query or ask a question to visualize outputs.</p>
      </div>
    `;
    queryStatsBar.style.display = "none";
    explanationText.textContent = "No queries generated yet. Ask a question to analyze its logic.";
    switchTab("results-tab");
  }
  
  function switchTab(tabId) {
    tabButtons.forEach(btn => {
      if (btn.getAttribute("data-tab") === tabId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
    tabContents.forEach(content => {
      if (content.id === tabId) {
        content.classList.add("active");
      } else {
        content.classList.remove("active");
      }
    });
  }
});
