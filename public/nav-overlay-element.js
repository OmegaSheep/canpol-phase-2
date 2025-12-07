class NavOverlayElement extends HTMLElement {
    get #dialog() { return this.shadowRoot.querySelector("dialog"); }

    #internals = this.attachInternals();
    constructor() {
        super();
        this.attachShadow({ mode: "open" });

        this.shadowRoot.innerHTML = `
            <style>
                ::slotted(span) { pointer-events: none; }
                ::slotted(svg) { fill: currentColor; width: 1em; height: 1em; position: relative; top: -0.1em; vertical-align: middle; }
            </style>
            <button commandfor=overlay command=show-modal part="button open-button">
                <slot name=open-button-label></slot>
                <slot name=open-button-icon aria-hidden=true></slot>
            </button>
            <dialog id=overlay part=overlay>
                <button commandfor=overlay command=close part="button close-button">
                    <slot name=close-button-label></slot>
                    <slot name=close-button-icon aria-hidden=true></slot>
                </button>
                <slot></slot>
            </dialog>
        `;

        if (!("command" in HTMLButtonElement.prototype)) {
            this.shadowRoot.addEventListener("click", this);
        }

        this.shadowRoot.addEventListener("toggle", this, true);
    }

    handleEvent(event) {
        switch (event.type) {
            case "click":
                if (event.target?.part.contains("open-button")) this.#dialog.showModal();
                if (event.target?.part.contains("close-button")) this.#dialog.close();
                break;
            case "toggle":
                this.#internals.states[event.newState === "open" ? "add" : "delete"]("open");
                break;
        }
    }
}

customElements.define("nav-overlay", NavOverlayElement);
