/**
 * YourClean — Premium Calculator v3.0
 * Step-based calculator with calendar, service types, and WhatsApp integration
 */

class Calculator {
    constructor() {
        // State
        this.currentStep = 1;
        this.selectedDate = null;
        this.selectedDiscount = 0;
        this.serviceType = 'cleaning'; // 'cleaning', 'drycleaning', 'cargo', 'shoe_cleaning'
        this.level = 'basic';
        this.area = 50;
        this.extraServices = [];
        this.drycleaningItems = {};
        this.discounts = {};
        this.isSubmitting = false;

        // Cargo state
        this.cargoTariffId = null;
        this.cargoHours = 2;
        this.cargoOptions = [];
        this.cargoTariffsData = [];
        this.cargoOptionsData = [];

        // Shoe cleaning state
        this.shoeCleaningItems = {};
        this.shoeCleaningData = [];

        // Calendar state
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();

        const calculatorSection = document.getElementById('calculator');
        const data = calculatorSection?.dataset || {};
        this.i18n = {
            discountLabel: data.discountLabel || 'Скидка',
            discountOnDate: data.discountOnDate || 'Скидка __PERCENT__% на эту дату!',
            summaryDate: data.summaryDateLabel || 'Дата',
            summaryService: data.summaryServiceLabel || 'Тип услуги',
            summaryLevel: data.summaryLevelLabel || 'Уровень',
            summaryArea: data.summaryAreaLabel || 'Площадь',
            summaryDiscount: data.summaryDiscountLabel || 'Скидка',
            serviceCleaningName: data.serviceCleaningName || 'Уборка',
            serviceDrycleaningName: data.serviceDrycleaningName || 'Химчистка',
            serviceCargoName: data.serviceCargoName || 'Грузоперевозки',
            serviceShoeName: data.serviceShoeName || 'Химчистка обуви',
            summaryExtra: data.summaryExtraLabel || 'Дополнительные услуги',
            summaryExtraEmpty: data.summaryExtraEmpty || 'Дополнительные услуги не выбраны',
            summaryDry: data.summaryDryLabel || 'Объекты химчистки',
            summaryDryEmpty: data.summaryDryEmpty || 'Химчистка не выбрана',
            summaryTariff: data.summaryTariffLabel || 'Тариф',
            summaryHours: data.summaryHoursLabel || 'Часы',
            summaryCargoOptions: data.summaryCargoOptionsLabel || 'Доп. опции',
            summaryShoeItems: data.summaryShoeItemsLabel || 'Обувь',
            areaUnit: data.areaUnit || 'м²',
            unitPiece: data.unitPiece || 'шт'
        };

        this.monthNames = this.getMonthNames();

        this.init();
    }

    getMonthNames() {
        const container = document.getElementById('calendar-container');
        if (container && container.dataset.monthNames) {
            try {
                const parsed = JSON.parse(container.dataset.monthNames);
                if (Array.isArray(parsed) && parsed.length === 12) {
                    return parsed;
                }
            } catch (error) {
                console.warn('Unable to parse localized month names:', error);
            }
        }

        // Fallback to Russian names
        return ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
    }

    async init() {
        await this.loadDiscounts();
        await Promise.all([
            this.loadServices(),
            this.loadCargoData(),
            this.loadShoeCleaningData(),
        ]);

        this.bindEvents();
        this.renderCalendar();
        this.updateStepIndicator();
    }

    // ==================== API Calls ====================

    async loadDiscounts() {
        try {
            const response = await fetch('/api/calendar-discounts/');
            this.discounts = await response.json();
        } catch (error) {
            console.error('Error loading discounts:', error);
        }
    }

    async loadServices() {
        try {
            const response = await fetch('/api/services/');
            const data = await response.json();
            this.extraServicesData = data.extra_services || [];
            this.drycleaningServicesData = data.dry_cleaning_services || [];
            this.renderExtraServices();
            this.renderDrycleaningItems();
        } catch (error) {
            console.error('Error loading services:', error);
        }
    }

    async loadCargoData() {
        try {
            const response = await fetch('/api/cargo/');
            const data = await response.json();
            this.cargoTariffsData = data.tariffs || [];
            this.cargoOptionsData = data.options || [];
            this.renderCargoTariffs();
            this.renderCargoOptions();
        } catch (error) {
            console.error('Error loading cargo data:', error);
        }
    }

    async loadShoeCleaningData() {
        try {
            const response = await fetch('/api/shoe-cleaning/');
            const data = await response.json();
            this.shoeCleaningData = data.services || [];
            this.renderShoeCleaningItems();
        } catch (error) {
            console.error('Error loading shoe cleaning data:', error);
        }
    }

    // ==================== Calendar ====================

    renderCalendar() {
        const titleEl = document.getElementById('calendar-title');
        const daysEl = document.getElementById('calendar-days');

        if (!titleEl || !daysEl) return;

        titleEl.textContent = `${this.monthNames[this.currentMonth]} ${this.currentYear}`;

        const firstDay = new Date(this.currentYear, this.currentMonth, 1);
        const lastDay = new Date(this.currentYear, this.currentMonth + 1, 0);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // Day of week for first day (0 = Sunday, we need Monday = 0)
        let startDay = firstDay.getDay() - 1;
        if (startDay < 0) startDay = 6;

        let html = '';

        // Empty cells for days before first day
        for (let i = 0; i < startDay; i++) {
            html += '<div class="calendar-day empty"></div>';
        }

        // Days of month
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const date = new Date(this.currentYear, this.currentMonth, day);
            const dateStr = this.formatDate(date);
            const isPast = date < today;
            const isToday = date.getTime() === today.getTime();
            const isSelected = this.selectedDate === dateStr;
            const discountPercent = this.discounts[dateStr] || 0;
            const hasDiscount = discountPercent > 0;

            let classes = ['calendar-day'];
            if (isPast) classes.push('disabled');
            if (isToday) classes.push('today');
            if (isSelected) classes.push('selected');
            if (hasDiscount) classes.push('has-discount');

            // Добавляем процент скидки на дату
            let discountBadge = '';
            if (hasDiscount && !isSelected) {
                discountBadge = `<span class="calendar-day__discount">-${discountPercent}%</span>`;
            }

            html += `<div class="${classes.join(' ')}" data-date="${dateStr}" data-discount="${discountPercent}">
                ${day}
                ${discountBadge}
            </div>`;
        }

        daysEl.innerHTML = html;

        // Bind day clicks
        daysEl.querySelectorAll('.calendar-day:not(.disabled):not(.empty)').forEach(el => {
            el.addEventListener('click', () => this.selectDate(el.dataset.date));
        });
    }

    selectDate(dateStr) {
        this.selectedDate = dateStr;
        this.selectedDiscount = this.discounts[dateStr] || 0;

        // Update calendar
        document.querySelectorAll('.calendar-day').forEach(el => {
            el.classList.toggle('selected', el.dataset.date === dateStr);
        });

        // Update info
        const infoEl = document.getElementById('selected-date-info');
        const dateDisplay = document.getElementById('selected-date-display');
        const discountDisplay = document.getElementById('selected-date-discount');

        if (infoEl && dateDisplay) {
            const date = new Date(dateStr);
            dateDisplay.textContent = `📅 ${date.getDate()} ${this.monthNames[date.getMonth()]} ${date.getFullYear()}`;

            if (this.selectedDiscount > 0) {
                discountDisplay.textContent = `🎉 ${this.i18n.discountOnDate.replace('__PERCENT__', this.selectedDiscount)}`;
                discountDisplay.style.display = 'block';
            } else {
                discountDisplay.style.display = 'none';
            }

            infoEl.style.display = 'block';
        }

        // Enable next button
        const nextBtn = document.getElementById('step1-next');
        if (nextBtn) nextBtn.disabled = false;
    }

    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // ==================== Services Rendering ====================

    renderExtraServices() {
        const container = document.getElementById('extra-services');
        if (!container || !this.extraServicesData) return;

        container.innerHTML = this.extraServicesData.map(service => `
            <label class="extra-service-item" data-id="${service.id}">
                <span class="extra-service-item__checkbox">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M20 6L9 17l-5-5"/>
                    </svg>
                </span>
                <div class="extra-service-item__info">
                    <div class="extra-service-item__name">${service.name}</div>
                    <div class="extra-service-item__price">
                        ${service.price_type === 'fixed'
                ? `${service.price} Kč`
                : `${service.price} Kč/м²`}
                    </div>
                </div>
            </label>
        `).join('');

        container.querySelectorAll('.extra-service-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                item.classList.toggle('selected');
                this.updateSelectedServices();
                this.calculatePrice();
            });
        });
    }

    renderDrycleaningItems() {
        const container = document.getElementById('drycleaning-items');
        if (!container || !this.drycleaningServicesData) return;

        container.innerHTML = this.drycleaningServicesData.map(service => `
            <div class="drycleaning-item-row" data-id="${service.id}">
                <div class="drycleaning-item-row__info">
                    <div class="drycleaning-item-row__name">${service.name}</div>
                    <div class="drycleaning-item-row__price">
                        ${service.unit === 'm2' ? `${service.price} Kč/м²` : `${service.price} Kč`}
                    </div>
                </div>
                <div class="drycleaning-item-row__quantity">
                    <input type="number" min="0" value="0" data-id="${service.id}" 
                           data-unit="${service.unit}" class="form__input">
                    <span>${service.unit === 'm2' ? 'м²' : 'шт'}</span>
                </div>
            </div>
        `).join('');

        container.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => {
                const id = input.dataset.id;
                const value = parseFloat(input.value) || 0;
                if (value > 0) {
                    this.drycleaningItems[id] = value;
                } else {
                    delete this.drycleaningItems[id];
                }
                this.calculatePrice();
            });
        });
    }

    updateSelectedServices() {
        const container = document.getElementById('extra-services');
        if (!container) return;

        this.extraServices = Array.from(container.querySelectorAll('.extra-service-item.selected'))
            .map(item => parseInt(item.dataset.id, 10));
    }

    renderCargoTariffs() {
        const container = document.getElementById('cargo-tariffs');
        if (!container || !this.cargoTariffsData.length) return;

        container.innerHTML = this.cargoTariffsData.map((tariff, idx) => `
            <label class="extra-service-item${idx === 0 ? ' selected' : ''}" data-id="${tariff.id}">
                <span class="extra-service-item__checkbox">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M20 6L9 17l-5-5"/>
                    </svg>
                </span>
                <div class="extra-service-item__info">
                    <div class="extra-service-item__name">${tariff.name}</div>
                    <div class="extra-service-item__price">${tariff.price_per_hour} Kč/час (мин. ${tariff.min_hours} ч.)</div>
                </div>
            </label>
        `).join('');

        if (this.cargoTariffsData.length > 0) {
            this.cargoTariffId = this.cargoTariffsData[0].id;
        }

        container.querySelectorAll('.extra-service-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                container.querySelectorAll('.extra-service-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                this.cargoTariffId = parseInt(item.dataset.id, 10);
                this.calculatePrice();
            });
        });
    }

    renderCargoOptions() {
        const container = document.getElementById('cargo-options');
        if (!container || !this.cargoOptionsData.length) return;

        container.innerHTML = this.cargoOptionsData.map(option => `
            <label class="extra-service-item" data-id="${option.id}">
                <span class="extra-service-item__checkbox">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M20 6L9 17l-5-5"/>
                    </svg>
                </span>
                <div class="extra-service-item__info">
                    <div class="extra-service-item__name">${option.name}</div>
                    <div class="extra-service-item__price">${option.price} Kč</div>
                </div>
            </label>
        `).join('');

        container.querySelectorAll('.extra-service-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                item.classList.toggle('selected');
                this.cargoOptions = Array.from(container.querySelectorAll('.extra-service-item.selected'))
                    .map(i => parseInt(i.dataset.id, 10));
                this.calculatePrice();
            });
        });
    }

    renderShoeCleaningItems() {
        const container = document.getElementById('shoe-cleaning-items');
        if (!container || !this.shoeCleaningData.length) return;

        container.innerHTML = this.shoeCleaningData.map(service => `
            <div class="drycleaning-item-row" data-id="${service.id}">
                <div class="drycleaning-item-row__info">
                    <div class="drycleaning-item-row__name">${service.name}</div>
                    <div class="drycleaning-item-row__price">${service.price_per_pair} Kč/пара</div>
                </div>
                <div class="drycleaning-item-row__quantity">
                    <input type="number" min="0" value="0" data-id="${service.id}" class="form__input">
                    <span>пар</span>
                </div>
            </div>
        `).join('');

        container.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => {
                const id = input.dataset.id;
                const value = parseInt(input.value) || 0;
                if (value > 0) {
                    this.shoeCleaningItems[id] = value;
                } else {
                    delete this.shoeCleaningItems[id];
                }
                this.calculatePrice();
            });
        });
    }

    // ==================== Step Navigation ====================

    goToStep(step) {
        // Hide all steps
        document.querySelectorAll('.calculator-step').forEach(el => {
            el.style.display = 'none';
        });

        // Show target step
        const targetStep = document.getElementById(`step-${step}`);
        if (targetStep) {
            targetStep.style.display = 'block';
        }

        this.currentStep = step;
        this.updateStepIndicator();
        this.scrollToCalculatorTop();

        // Update parameters visibility based on service type
        if (step === 3) {
            const panels = {
                'cleaning': document.getElementById('cleaning-params'),
                'drycleaning': document.getElementById('drycleaning-params'),
                'cargo': document.getElementById('cargo-params'),
                'shoe_cleaning': document.getElementById('shoe-cleaning-params'),
            };
            Object.entries(panels).forEach(([key, el]) => {
                if (el) el.style.display = key === this.serviceType ? 'block' : 'none';
            });

            this.calculatePrice();
        }

        // Build order summary on step 4
        if (step === 4) {
            this.buildOrderSummary();
        }
    }

    scrollToCalculatorTop() {
        const calculatorSection = document.getElementById('calculator');
        if (!calculatorSection) return;

        const header = document.getElementById('header');
        const headerHeight = header ? header.offsetHeight : 0;
        const topOffset = calculatorSection.getBoundingClientRect().top + window.scrollY - headerHeight - 16;

        window.scrollTo({
            top: Math.max(topOffset, 0),
            behavior: 'smooth'
        });
    }

    updateStepIndicator() {
        document.querySelectorAll('.step-item').forEach(el => {
            const stepNum = parseInt(el.dataset.step, 10);
            el.classList.remove('active', 'completed');

            if (stepNum === this.currentStep) {
                el.classList.add('active');
            } else if (stepNum < this.currentStep) {
                el.classList.add('completed');
            }
        });
    }

    // ==================== Price Calculation ====================

    async calculatePrice() {
        const priceDisplay = document.getElementById('current-price');
        const oldPriceDisplay = document.getElementById('old-price');
        const discountInfo = document.getElementById('discount-info');

        if (!priceDisplay) return;

        priceDisplay.innerHTML = '<span class="spinner"></span>';

        try {
            let finalPrice = 0;
            let apiOldPrice = null;

            if (this.serviceType === 'cargo') {
                // Local calculation for cargo
                const tariff = this.cargoTariffsData.find(t => t.id === this.cargoTariffId);
                if (tariff) {
                    const minH = parseFloat(tariff.min_hours) || 1;
                    const hours = Math.max(this.cargoHours, minH);
                    finalPrice = parseFloat(tariff.price_per_hour) * hours;
                }
                for (const optId of this.cargoOptions) {
                    const opt = this.cargoOptionsData.find(o => o.id === optId);
                    if (opt) finalPrice += parseFloat(opt.price);
                }
            } else if (this.serviceType === 'shoe_cleaning') {
                // Local calculation for shoe cleaning
                for (const [id, qty] of Object.entries(this.shoeCleaningItems)) {
                    const svc = this.shoeCleaningData.find(s => String(s.id) === String(id));
                    if (svc && qty > 0) {
                        finalPrice += parseFloat(svc.price_per_pair) * qty;
                    }
                }
            } else {
                // API calculation for cleaning / drycleaning
                let params;
                if (this.serviceType === 'cleaning') {
                    params = new URLSearchParams({
                        level: this.level,
                        area: this.area,
                        rooms: 0,
                        bathrooms: 0,
                        extra_services: JSON.stringify(this.extraServices)
                    });
                } else {
                    params = new URLSearchParams({
                        level: 'basic',
                        area: 0,
                        rooms: 0,
                        bathrooms: 0,
                        dry_cleaning: JSON.stringify(this.drycleaningItems)
                    });
                }

                const response = await fetch(`/api/price/?${params}`);
                const data = await response.json();

                if (data.error) {
                    priceDisplay.textContent = '—';
                    console.error('Price calculation error:', data.error);
                    return;
                }
                finalPrice = parseFloat(data.price);
                if (data.old_price) apiOldPrice = parseFloat(data.old_price);
            }

            let originalPrice = finalPrice;

            // Apply date discount
            if (this.selectedDiscount > 0) {
                finalPrice = finalPrice * (1 - this.selectedDiscount / 100);
            }

            const formattedPrice = new Intl.NumberFormat('ru-RU', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(Math.round(finalPrice));

            priceDisplay.textContent = `${formattedPrice} Kč`;

            // Store for order
            this.calculatedPrice = Math.round(finalPrice);
            this.originalPrice = Math.round(originalPrice);

            // Show old price if discount
            if (this.selectedDiscount > 0) {
                oldPriceDisplay.textContent = `${Math.round(originalPrice)} Kč`;
                oldPriceDisplay.style.display = 'block';
                discountInfo.textContent = `${this.i18n.discountLabel} ${this.selectedDiscount}%`;
                discountInfo.style.display = 'block';
            } else if (apiOldPrice) {
                oldPriceDisplay.textContent = `${Math.round(apiOldPrice)} Kč`;
                oldPriceDisplay.style.display = 'block';
                discountInfo.style.display = 'none';
            } else {
                oldPriceDisplay.style.display = 'none';
                discountInfo.style.display = 'none';
            }

        } catch (error) {
            console.error('Error calculating price:', error);
            priceDisplay.textContent = '—';
        }
    }

    // ==================== Order ====================

    buildOrderSummary() {
        const itemsEl = document.getElementById('order-summary-items');
        const totalEl = document.getElementById('order-summary-total');

        if (!itemsEl || !totalEl) return;

        let html = '';

        // Date
        if (this.selectedDate) {
            const date = new Date(this.selectedDate);
            html += `<div class="order-summary__item">
                <span>📅 ${this.i18n.summaryDate}</span>
                <span>${date.getDate()} ${this.monthNames[date.getMonth()]}</span>
            </div>`;
        }

        // Service type
        const serviceNames = {
            cleaning: this.i18n.serviceCleaningName,
            drycleaning: this.i18n.serviceDrycleaningName,
            cargo: this.i18n.serviceCargoName,
            shoe_cleaning: this.i18n.serviceShoeName,
        };
        html += `<div class="order-summary__item">
            <span>🧹 ${this.i18n.summaryService}</span>
            <span>${serviceNames[this.serviceType] || this.serviceType}</span>
        </div>`;

        if (this.serviceType === 'cleaning') {
            // Level
            const levelNames = { basic: 'BASIC', general: 'GENERAL', general_plus: 'GENERAL+' };
            html += `<div class="order-summary__item">
                <span>📋 ${this.i18n.summaryLevel}</span>
                <span>${levelNames[this.level]}</span>
            </div>`;

            // Area
            html += `<div class="order-summary__item">
                <span>📐 ${this.i18n.summaryArea}</span>
                <span>${this.area} ${this.i18n.areaUnit}</span>
            </div>`;

            // Extra services
            const selectedExtras = (this.extraServices || [])
                .map(id => (this.extraServicesData || []).find(service => service.id === id))
                .filter(Boolean);

            const extrasContent = selectedExtras.length
                ? `<ul class="order-summary__list">${selectedExtras.map(service => {
                    const priceDisplay = service.price_type === 'fixed'
                        ? `${service.price} Kč`
                        : `${service.price} Kč/${this.i18n.areaUnit}`;
                    return `<li>${service.name} — ${priceDisplay}</li>`;
                }).join('')}</ul>`
                : `<em>${this.i18n.summaryExtraEmpty}</em>`;

            html += `<div class="order-summary__item order-summary__item--column">
                <span>✨ ${this.i18n.summaryExtra}</span>
                <div>${extrasContent}</div>
            </div>`;
        }

        // Dry cleaning items
        if (this.serviceType === 'drycleaning') {
            const dryItemsEntries = Object.entries(this.drycleaningItems || {})
                .filter(([, qty]) => parseFloat(qty) > 0);
            if (dryItemsEntries.length) {
                const dryList = dryItemsEntries
                    .map(([id, qty]) => {
                        const service = (this.drycleaningServicesData || []).find(item => String(item.id) === String(id));
                        if (!service) return null;
                        const unitLabel = service.unit === 'm2' ? this.i18n.areaUnit : this.i18n.unitPiece;
                        return `<li>${service.name} — ${qty} ${unitLabel}</li>`;
                    })
                    .filter(Boolean);

                const dryContent = dryList.length
                    ? `<ul class="order-summary__list">${dryList.join('')}</ul>`
                    : `<em>${this.i18n.summaryDryEmpty}</em>`;

                html += `<div class="order-summary__item order-summary__item--column">
                    <span>🧼 ${this.i18n.summaryDry}</span>
                    <div>${dryContent}</div>
                </div>`;
            }
        }

        // Cargo summary
        if (this.serviceType === 'cargo') {
            const tariff = this.cargoTariffsData.find(t => t.id === this.cargoTariffId);
            if (tariff) {
                html += `<div class="order-summary__item">
                    <span>🚚 ${this.i18n.summaryTariff}</span>
                    <span>${tariff.name}</span>
                </div>`;
                html += `<div class="order-summary__item">
                    <span>⏱ ${this.i18n.summaryHours}</span>
                    <span>${this.cargoHours} ч.</span>
                </div>`;
            }
            if (this.cargoOptions.length) {
                const optList = this.cargoOptions
                    .map(id => this.cargoOptionsData.find(o => o.id === id))
                    .filter(Boolean)
                    .map(o => `<li>${o.name} — ${o.price} Kč</li>`);
                html += `<div class="order-summary__item order-summary__item--column">
                    <span>📦 ${this.i18n.summaryCargoOptions}</span>
                    <div><ul class="order-summary__list">${optList.join('')}</ul></div>
                </div>`;
            }
        }

        // Shoe cleaning summary
        if (this.serviceType === 'shoe_cleaning') {
            const shoeEntries = Object.entries(this.shoeCleaningItems || {}).filter(([, qty]) => qty > 0);
            if (shoeEntries.length) {
                const shoeList = shoeEntries
                    .map(([id, qty]) => {
                        const svc = this.shoeCleaningData.find(s => String(s.id) === String(id));
                        return svc ? `<li>${svc.name} — ${qty} пар</li>` : null;
                    })
                    .filter(Boolean);
                html += `<div class="order-summary__item order-summary__item--column">
                    <span>👟 ${this.i18n.summaryShoeItems}</span>
                    <div><ul class="order-summary__list">${shoeList.join('')}</ul></div>
                </div>`;
            }
        }

        // Discount
        if (this.selectedDiscount > 0) {
            html += `<div class="order-summary__item" style="color: var(--color-accent);">
                <span>🎉 ${this.i18n.summaryDiscount}</span>
                <span>-${this.selectedDiscount}%</span>
            </div>`;
        }

        itemsEl.innerHTML = html;
        totalEl.textContent = `${this.calculatedPrice || 0} Kč`;
    }

    getCsrfToken() {
        const name = 'csrftoken=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookies = decodedCookie.split(';');
        for (let cookie of cookies) {
            let c = cookie.trim();
            if (c.startsWith(name)) {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    }

    ensureCzechPhonePrefix(phoneValue) {
        const digits = (phoneValue || '').replace(/[^0-9]/g, '');
        let national = digits;
        if (national.startsWith('420')) {
            national = national.slice(3);
        }
        const formatted = national ? `+420 ${national}` : '+420 ';
        return formatted.trim();
    }

    setSubmittingState(isSubmitting) {
        this.isSubmitting = isSubmitting;
        const submitBtn = document.getElementById('submit-order');
        if (submitBtn) {
            submitBtn.disabled = isSubmitting;
            submitBtn.classList.toggle('btn--loading', isSubmitting);
            submitBtn.setAttribute('aria-busy', isSubmitting ? 'true' : 'false');
        }
    }

    async submitOrder() {
        if (this.isSubmitting) {
            return;
        }

        this.setSubmittingState(true);

        const nameInput = document.getElementById('name');
        const phoneInput = document.getElementById('phone');
        const addressInput = document.getElementById('address');
        const timeInput = document.getElementById('time');
        const commentInput = document.getElementById('comment');

        // Validate
        if (!nameInput.value.trim() || !phoneInput.value.trim()) {
            alert('Пожалуйста, заполните имя и телефон');
            this.setSubmittingState(false);
            return;
        }

        const formattedPhone = this.ensureCzechPhonePrefix(phoneInput.value.trim());
        phoneInput.value = formattedPhone;

        // Try to save order to backend (и далее в Google Sheets)
        try {
            const orderData = {
                name: nameInput.value,
                phone: formattedPhone,
                address: addressInput.value || null,
                level: this.serviceType === 'cleaning' ? this.level : 'basic',
                area: this.serviceType === 'cleaning' ? this.area : 1,
                rooms: 0,
                bathrooms: 0,
                total_price: this.calculatedPrice,
                desired_date: this.selectedDate || null,
                desired_time: timeInput.value || null,
                applied_discount_percent: this.selectedDiscount,
                comment: commentInput.value || null,
                service_type: this.serviceType,
                extra_services: this.extraServices,
                dry_cleaning_items: this.drycleaningItems
            };

            const response = await fetch('/api/orders/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                credentials: 'same-origin',
                body: JSON.stringify(orderData)
            });

            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Не удалось сохранить заявку');
            }
        } catch (error) {
            console.error('Error saving order:', error);
            alert('Не удалось сохранить заявку. Попробуйте ещё раз или свяжитесь с нами по телефону.');
            this.setSubmittingState(false);
            return;
        }

        // Show success
        document.querySelectorAll('.calculator-step').forEach(el => el.style.display = 'none');
        document.getElementById('order-success').style.display = 'block';
        this.scrollToCalculatorTop();
        this.setSubmittingState(false);
    }

    // ==================== Event Binding ====================

    bindEvents() {
        // Calendar navigation
        document.getElementById('calendar-prev')?.addEventListener('click', () => {
            this.currentMonth--;
            if (this.currentMonth < 0) {
                this.currentMonth = 11;
                this.currentYear--;
            }
            this.renderCalendar();
        });

        document.getElementById('calendar-next')?.addEventListener('click', () => {
            this.currentMonth++;
            if (this.currentMonth > 11) {
                this.currentMonth = 0;
                this.currentYear++;
            }
            this.renderCalendar();
        });

        // Step navigation
        document.getElementById('step1-next')?.addEventListener('click', () => this.goToStep(2));
        document.getElementById('step2-prev')?.addEventListener('click', () => this.goToStep(1));
        document.getElementById('step2-next')?.addEventListener('click', () => this.goToStep(3));
        document.getElementById('step3-prev')?.addEventListener('click', () => this.goToStep(2));
        document.getElementById('step3-next')?.addEventListener('click', () => this.goToStep(4));
        document.getElementById('step4-prev')?.addEventListener('click', () => this.goToStep(3));

        // Service type selection
        document.querySelectorAll('input[name="service_type"]').forEach(input => {
            input.addEventListener('change', () => {
                this.serviceType = input.value;
            });
        });

        // Cargo hours input
        const cargoHoursInput = document.getElementById('cargo-hours');
        if (cargoHoursInput) {
            cargoHoursInput.addEventListener('input', () => {
                this.cargoHours = parseFloat(cargoHoursInput.value) || 1;
                this.debounceCalculate();
            });
        }

        // Level tabs
        document.querySelectorAll('#level-tabs .tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('#level-tabs .tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.level = tab.dataset.level;

                document.querySelectorAll('.level-description').forEach(desc => {
                    desc.classList.toggle('active', desc.dataset.level === this.level);
                });

                this.calculatePrice();
            });
        });

        // Area input
        const areaInput = document.getElementById('area');
        const areaSlider = document.getElementById('area-slider');

        if (areaInput) {
            areaInput.addEventListener('input', () => {
                this.area = Math.max(1, parseInt(areaInput.value, 10) || 0);
                if (areaSlider) areaSlider.value = Math.min(Math.max(this.area, 20), 200);
                this.debounceCalculate();
            });
        }

        if (areaSlider) {
            areaSlider.addEventListener('input', () => {
                this.area = parseInt(areaSlider.value, 10);
                if (areaInput) areaInput.value = this.area;
                this.updateSliderBackground(areaSlider);
                this.debounceCalculate();
            });
            this.updateSliderBackground(areaSlider);
        }

        // Order submit
        document.getElementById('submit-order')?.addEventListener('click', () => {
            this.submitOrder();
        });

        this.initTimeInputMask();
    }

    initTimeInputMask() {
        const timeInput = document.getElementById('time');
        if (!timeInput) return;

        const formatValue = (raw) => {
            const digits = raw.replace(/[^0-9]/g, '').slice(0, 4);
            if (digits.length <= 2) {
                return digits;
            }
            return `${digits.slice(0, 2)}:${digits.slice(2)}`;
        };

        timeInput.addEventListener('input', () => {
            const caret = timeInput.selectionStart;
            const beforeLength = timeInput.value.length;
            timeInput.value = formatValue(timeInput.value);
            const afterLength = timeInput.value.length;
            const diff = afterLength - beforeLength;
            timeInput.setSelectionRange(caret + diff, caret + diff);
        });

        timeInput.addEventListener('blur', () => {
            let digits = timeInput.value.replace(/[^0-9]/g, '');
            if (!digits) {
                timeInput.value = '';
                return;
            }

            while (digits.length < 4) {
                digits += '0';
            }

            const hours = Math.min(parseInt(digits.slice(0, 2), 10) || 0, 23)
                .toString()
                .padStart(2, '0');
            const minutes = Math.min(parseInt(digits.slice(2, 4), 10) || 0, 59)
                .toString()
                .padStart(2, '0');

            timeInput.value = `${hours}:${minutes}`;
        });
    }

    updateSliderBackground(slider) {
        const min = parseInt(slider.min, 10);
        const max = parseInt(slider.max, 10);
        const value = parseInt(slider.value, 10);
        const percentage = ((value - min) / (max - min)) * 100;
        slider.style.setProperty('--value', `${percentage}%`);
    }

    debounceCalculate() {
        clearTimeout(this.calculateTimeout);
        this.calculateTimeout = setTimeout(() => this.calculatePrice(), 300);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if on calculator page
    if (document.getElementById('calculator')) {
        new Calculator();
    }
});
