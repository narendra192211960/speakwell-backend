/**
 * SpeakWell Single Page Router
 * Handles dynamic content loading into the main application container.
 */

const Router = {
    contentArea: null,
    loader: null,
    currentPage: null,

    init() {
        this.contentArea = document.getElementById('mainContent');
        this.loader = document.getElementById('pageLoader');
        
        // Listen for navigation clicks
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.currentTarget.getAttribute('data-page');
                this.navigate(page);
            });
        });

        // Handle browser back/forward
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.loadPage(e.state.page, false, e.state);
            }
        });


        // Logout listener
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                if (typeof Auth !== 'undefined') {
                    Auth.logout();
                } else {
                    localStorage.clear();
                    window.location.href = 'login.html';
                }
            });
        }

        // Initial page load
        const initialPage = new URLSearchParams(window.location.search).get('page') || 'home';
        this.navigate(initialPage, true);
    },

    navigate(page, isInitial = false) {
        if (this.currentPage === page && !isInitial) {
            // Trigger an event to allow the current page to reset/refresh
            window.dispatchEvent(new CustomEvent('pageLoaded', { detail: { page: this.currentPage, renav: true } }));
            return;
        }
        
        this.loadPage(page, !isInitial);
        
        // Update active state in sidebar
        document.querySelectorAll('[data-page]').forEach(link => {
            if (link.getAttribute('data-page') === page) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },

    cache: {},

    async loadPage(page, pushState = true, state = null) {
        if (this.currentPage === page && !pushState && !state) return;
        this.currentPage = page;
        this.currentState = state;

        
        // Check cache first for immediate load
        if (this.cache[page]) {
            this.renderPage(this.cache[page]);
            this.updateHistory(page, pushState);
            return;
        }

        // Check for embedded templates (file:// protocol compatibility)
        const template = document.getElementById(`tpl-${page}`);
        if (template) {
            const html = template.innerHTML;
            this.cache[page] = html;
            this.renderPage(html);
            this.updateHistory(page, pushState);
            return;
        }

        this.showLoader();

        try {
            const response = await fetch(`${page}.html`);
            if (!response.ok) throw new Error('Page not found');
            
            const html = await response.text();
            this.cache[page] = html; // Store in cache
            
            this.renderPage(html);
            this.updateHistory(page, pushState);

        } catch (error) {
            console.error('Routing Error:', error);
            this.contentArea.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--error);">
                <svg viewBox="0 0 24 24" width="60" height="60" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 20px;">
                    <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <h2 style="font-size: 2rem; font-weight: 800; margin-bottom: 10px;">Error loading page</h2>
                <p style="color: var(--text-muted); font-size: 1.1rem;">${error.message}</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">If you are opening this as a file, please use a local web server.</p>
                <button class="btn-primary" onclick="window.location.reload()" style="margin-top: 30px; width: auto; padding: 12px 30px;">Try Refreshing</button>
            </div>`;
        } finally {
            this.hideLoader();
        }
    },

    renderPage(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const content = doc.querySelector('.main-wrapper') || doc.querySelector('.main-content') || doc.body;
        
        this.contentArea.innerHTML = '';
        
        // Inject styles
        doc.querySelectorAll('style').forEach(style => {
            this.contentArea.appendChild(style.cloneNode(true));
        });

        this.contentArea.appendChild(content.cloneNode(true));

        // Inject scripts
        doc.querySelectorAll('script').forEach(oldScript => {
            const newScript = document.createElement('script');
            if (oldScript.src) {
                newScript.src = oldScript.src;
            } else {
                newScript.textContent = oldScript.textContent;
            }
            document.body.appendChild(newScript);
        });

        // Re-bind links inside the new content
        this.contentArea.querySelectorAll('[data-page]').forEach(link => {
            link.onclick = (e) => {
                e.preventDefault();
                this.navigate(link.getAttribute('data-page'));
            };
        });

        window.dispatchEvent(new CustomEvent('pageLoaded', { 
            detail: { 
                page: this.currentPage, 
                state: this.currentState 
            } 
        }));

    },

    updateHistory(page, pushState) {
        if (pushState) {
            const url = new URL(window.location);
            url.searchParams.set('page', page);
            const state = { page };
            this.currentState = state; // Track current state locally
            window.history.pushState(state, '', url);
        }
    },


    showLoader() {
        if (this.loader) this.loader.style.display = 'block';
    },

    hideLoader() {
        if (this.loader) this.loader.style.display = 'none';
    }
};

window.addEventListener('DOMContentLoaded', () => Router.init());
window.Router = Router;
