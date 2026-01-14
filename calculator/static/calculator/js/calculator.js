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
        this.serviceType = 'cleaning'; // 'cleaning' or 'drycleaning'
        this.level = 'basic';
        this.area = 50;
        this.extraServices = [];
        this.drycleaningItems = {};
        this.discounts = {};

        // Calendar state
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();

        // Месяцы на русском
        this.monthNames = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ];

        this.init();
    }

    async init() {
        await this.loadDiscounts();
        await this.loadServices();

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
                discountDisplay.textContent = `🎉 Скидка ${this.selectedDiscount}% на эту дату!`;
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
                ? `${service.price} ₽`
                : `${service.price} ₽/м²`}
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
                        ${service.unit === 'm2' ? `${service.price} ₽/м²` : `${service.price} ₽`}
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

        // Update parameters visibility based on service type
        if (step === 3) {
            const cleaningParams = document.getElementById('cleaning-params');
            const drycleaningParams = document.getElementById('drycleaning-params');

            if (cleaningParams && drycleaningParams) {
                cleaningParams.style.display = this.serviceType === 'cleaning' ? 'block' : 'none';
                drycleaningParams.style.display = this.serviceType === 'drycleaning' ? 'block' : 'none';
            }

            this.calculatePrice();
        }

        // Build order summary on step 4
        if (step === 4) {
            this.buildOrderSummary();
        }
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

            let finalPrice = parseFloat(data.price);
            let originalPrice = finalPrice;

            // Apply date discount
            if (this.selectedDiscount > 0) {
                finalPrice = finalPrice * (1 - this.selectedDiscount / 100);
            }

            const formattedPrice = new Intl.NumberFormat('ru-RU', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(Math.round(finalPrice));

            priceDisplay.textContent = `${formattedPrice} ₽`;

            // Store for order
            this.calculatedPrice = Math.round(finalPrice);
            this.originalPrice = Math.round(originalPrice);

            // Show old price if discount
            if (this.selectedDiscount > 0) {
                oldPriceDisplay.textContent = `${Math.round(originalPrice)} ₽`;
                oldPriceDisplay.style.display = 'block';
                discountInfo.textContent = `Скидка ${this.selectedDiscount}%`;
                discountInfo.style.display = 'block';
            } else if (data.old_price) {
                oldPriceDisplay.textContent = `${Math.round(parseFloat(data.old_price))} ₽`;
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
                <span>📅 Дата</span>
                <span>${date.getDate()} ${this.monthNames[date.getMonth()]}</span>
            </div>`;
        }

        // Service type
        html += `<div class="order-summary__item">
            <span>🧹 Тип услуги</span>
            <span>${this.serviceType === 'cleaning' ? 'Уборка' : 'Химчистка'}</span>
        </div>`;

        if (this.serviceType === 'cleaning') {
            // Level
            const levelNames = { basic: 'BASIC', general: 'GENERAL', general_plus: 'GENERAL+' };
            html += `<div class="order-summary__item">
                <span>📋 Уровень</span>
                <span>${levelNames[this.level]}</span>
            </div>`;

            // Area
            html += `<div class="order-summary__item">
                <span>📐 Площадь</span>
                <span>${this.area} м²</span>
            </div>`;
        }

        // Discount
        if (this.selectedDiscount > 0) {
            html += `<div class="order-summary__item" style="color: var(--color-accent);">
                <span>🎉 Скидка</span>
                <span>-${this.selectedDiscount}%</span>
            </div>`;
        }

        itemsEl.innerHTML = html;
        totalEl.textContent = `${this.calculatedPrice || 0} ₽`;
    }

    async submitToWhatsApp() {
        const nameInput = document.getElementById('name');
        const phoneInput = document.getElementById('phone');
        const addressInput = document.getElementById('address');
        const timeInput = document.getElementById('time');
        const commentInput = document.getElementById('comment');

        // Validate
        if (!nameInput.value.trim() || !phoneInput.value.trim()) {
            alert('Пожалуйста, заполните имя и телефон');
            return;
        }

        // Build WhatsApp message
        const levelNames = { basic: 'BASIC', general: 'GENERAL', general_plus: 'GENERAL+' };
        const date = this.selectedDate ? new Date(this.selectedDate) : null;

        let message = `🧹 ЗАЯВКА НА ${this.serviceType === 'cleaning' ? 'УБОРКУ' : 'ХИМЧИСТКУ'}\n\n`;
        message += `👤 Имя: ${nameInput.value}\n`;
        message += `📞 Телефон: ${phoneInput.value}\n`;

        if (addressInput.value) {
            message += `📍 Адрес: ${addressInput.value}\n`;
        }

        message += `\n📋 ПАРАМЕТРЫ:\n`;

        if (date) {
            message += `📅 Дата: ${date.getDate()} ${this.monthNames[date.getMonth()]} ${date.getFullYear()}\n`;
        }

        if (timeInput.value) {
            message += `⏰ Время: ${timeInput.value}\n`;
        }

        if (this.serviceType === 'cleaning') {
            message += `🔹 Тип: ${levelNames[this.level]}\n`;
            message += `🔹 Площадь: ${this.area} м²\n`;
        } else {
            message += `🔹 Химчистка мебели\n`;
        }

        if (this.selectedDiscount > 0) {
            message += `🎉 Скидка: ${this.selectedDiscount}%\n`;
        }

        message += `\n💰 ИТОГО: ${this.calculatedPrice} ₽`;

        if (this.selectedDiscount > 0) {
            message += ` (было ${this.originalPrice} ₽)`;
        }

        if (commentInput.value) {
            message += `\n\n💬 Комментарий: ${commentInput.value}`;
        }

        // Get WhatsApp number
        const whatsappNumber = window.WHATSAPP_NUMBER || '';
        const cleanNumber = whatsappNumber.replace(/[^0-9]/g, '');

        if (!cleanNumber) {
            alert('WhatsApp номер не настроен');
            return;
        }

        // Try to save order to backend first
        try {
            const orderData = {
                name: nameInput.value,
                phone: phoneInput.value,
                address: addressInput.value || null,
                level: this.serviceType === 'cleaning' ? this.level : 'basic',
                area: this.serviceType === 'cleaning' ? this.area : 0,
                rooms: 0,
                bathrooms: 0,
                total_price: this.calculatedPrice,
                desired_date: this.selectedDate || null,
                desired_time: timeInput.value || null,
                applied_discount_percent: this.selectedDiscount,
                comment: commentInput.value || null
            };

            await fetch('/api/orders/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });
        } catch (error) {
            console.error('Error saving order:', error);
        }

        // Open WhatsApp
        const encodedMessage = encodeURIComponent(message);
        const whatsappUrl = `https://wa.me/${cleanNumber}?text=${encodedMessage}`;

        window.open(whatsappUrl, '_blank');

        // Show success
        document.querySelectorAll('.calculator-step').forEach(el => el.style.display = 'none');
        document.getElementById('order-success').style.display = 'block';
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

        // WhatsApp submit
        document.getElementById('submit-whatsapp')?.addEventListener('click', () => {
            this.submitToWhatsApp();
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
