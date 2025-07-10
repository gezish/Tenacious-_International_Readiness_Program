# Wee_2: Deliveries

<style>
.tabs {
  display: flex;
  margin-bottom: 1rem;
  cursor: pointer;
}
.tab-button {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  background: #f1f1f1;
  margin-right: 5px;
}
.tab-button.active {
  background: #fff;
  font-weight: bold;
}
.tab-content {
  display: none;
  padding: 1rem;
  border: 1px solid #ccc;
  background: #fff;
}
.tab-content.active {
  display: block;
}
</style>

<div class="tabs">
  <div class="tab-button active" onclick="showTab('tab1')" style="Bold">Urgent Snapshot Update</div>
  <div class="tab-button" onclick="showTab('tab2')" style="Bold">Tab 2</div>
  <div class="tab-button" onclick="showTab('tab3')">Tab 3</div>
</div>

<div id="tab1" class="tab-content active">
  <h3>Welcome to Tab 1</h3>
  <p>This is the first tab. You can include <strong>markdown-like HTML</strong>.</p>
</div>

<div id="tab2" class="tab-content">
  <h3>Welcome to Tab 2</h3>
  <p>Include more complex content like lists:</p>
  <ul>
    <li>Automation</li>
    <li>Monitoring</li>
    <li>CI/CD</li>
  </ul>
</div>

<div id="tab3" class="tab-content">
  <h3>Tab 3: Code Block</h3>
  <pre><code>print("Hello from Python!")</code></pre>
</div>

<script>
function showTab(tabId) {
  document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById(tabId).classList.add('active');
}
</script>
