document.addEventListener("DOMContentLoaded", function(e) {
    function buildURL(elem, query) {
        const url = new URL(window.location.origin + elem.getAttribute("data-autocomplete-url"));
        const searchParams = new URLSearchParams();
        searchParams.set("q", query && query !== undefined && query !== null ? query : "")
        if(elem.hasAttribute("data-dependent-fields")){ 
            const form = elem.closest('form');
            let dependentFields = elem.getAttribute("data-dependent-fields").split("__")
    
            for(let i=0; i < dependentFields.length; i++) {
                const field = form.querySelector(`[name=${dependentFields[i]}]`);
                if(field == null) continue;
                searchParams.set(dependentFields[i], field.value)
            }
        }
        if(elem.hasAttribute("data-get-params")){ 
            let getParams = JSON.parse(elem.getAttribute("data-get-params"))
            for(let [key, value] of Object.entries(getParams)) {
                searchParams.set(key, value)
    
            }
        }
        return url.toString() + "?" + searchParams.toString()
    }
    
    var tomSelects = {};
    function initTomSelect(elem) {
        if (Object.keys(tomSelects).includes(elem.id)) { 
            tomSelects[elem.id].destroy();
        }
        plugins = ['virtual_scroll', 'clear_button']
        if(elem.hasAttribute("multiple")) {
            plugins.push('remove_button');
        }
    
        tomSelects[elem.id] = new TomSelect(elem, {
            create: elem.hasAttribute("data-create"),
            preload: false,
            url: `${elem.getAttribute("data-autocomplete-url")}`,
            plugins: plugins,
            shouldLoad: function (query) {
                return true;
            },
            hideSelected: true,
            maxOptions: 99999,
            firstUrl: function (query) {
                return buildURL(elem , query);
            },
            load: function (query, callback) {
                let dependentFields = elem.getAttribute("data-dependent-fields")
                if(dependentFields != null) {
                    const form = elem.closest("form");
                    if (form) {
                        let allFieldsHaveValues = true;
                        for(let dependentField of dependentFields.split("__")) {
                            let field = form.querySelector(`[name="${dependentField}"]`)
                            if(field == null) continue;
    
                            let value = null;
                            if(field.hasAttribute('is-tomselect')) {
                                value = tomSelects[field.id].getValue()
                            } else {
                                value = field.value
                            }
                            if(value === '' || value === null || value === undefined) {
                                allFieldsHaveValues = false;
                            }
                        }
    
                        if(!allFieldsHaveValues) {
                            callback([])
                            return
                        }
                    } else {
                        console.error("FORM MISSING");
                    }
                }
    
                const url = this.getUrl(query);
                fetch(url)
                    .then(response => response.json())
                    .then(json => {
                        const _scrollToOption = this.scrollToOption
                        this.scrollToOption = () => {}
                        if (json.has_more) {
                            const next_url = buildURL(elem , query) + '&page=' + (json.page + 1);
                            this.setNextUrl(query, next_url);
                        }
                        const _isFocused = this.isFocused;
                        this.isFocused = false;
                        callback(json.results);
                        this.isFocused = _isFocused;
                        this.scrollToOption = _scrollToOption
    
                    }).catch((e) => {
                        callback();
                    });
            },
            onDropdownOpen: function() {
                tomSelects[elem.id].clearPagination();
                tomSelects[elem.id].clearOptions();
                tomSelects[elem.id].load('');
            },
            onDropdownClose: function() {
                tomSelects[elem.id].clearPagination();
                tomSelects[elem.id].clearOptions();
                tomSelects[elem.id].load('');
            },
            onChange: function(value) {
                tomSelects[elem.id].clearPagination();
                tomSelects[elem.id].clearOptions();
                tomSelects[elem.id].load('');
            },
        });
    
        let dependentFields = elem.getAttribute("data-dependent-fields")
        if(dependentFields != null) {
            const form = elem.closest("form");
            if (form) {
                for(let dependentField of dependentFields.split("__")) {
                    let field = form.querySelector(`[name="${dependentField}"]`)
                    if(!field) continue;
                    field.addEventListener("input", function(event) {
                        tomSelects[elem.id].clear();
                        tomSelects[elem.id].clearOptions();
                        tomSelects[elem.id].clearPagination();
                        tomSelects[elem.id].load('');
                    })
                }
            } else {
                console.error("FORM MISSING");
            }
        }
    }
    
    document.body.addEventListener('htmx:afterSettle', async (event) => {
        event.detail.target.querySelectorAll("[is-tomselect]").forEach((elem) => {
            initTomSelect(elem);
        });
    });

    for (const element of document.querySelectorAll(`[is-tomselect]`)) {
        initTomSelect(element);
    }
});
