class WorkCarousel {
    constructor(root) {
        this.root = root;
        this.track = root.querySelector('.work-carousel__track');
        this.slides = Array.from(root.querySelectorAll('.work-slide'));
        this.prevBtn = root.querySelector('[data-carousel-prev]');
        this.nextBtn = root.querySelector('[data-carousel-next]');
        this.tabs = Array.from(root.querySelectorAll('.work-carousel__tab'));
        this.dotsContainer = root.querySelector('.work-carousel__dots');

        this.currentIndex = 0;
        this.visibleSlides = [...this.slides];
        this.autoplayInterval = null;
        this.autoPlayDelay = 5000;

        this.bindEvents();
        this.buildDots();
        this.update();
        this.startAutoplay();
    }

    bindEvents() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prev());
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.next());
        }

        this.tabs.forEach((tab) => {
            tab.addEventListener('click', () => this.filterSlides(tab));
        });

        this.root.addEventListener('mouseenter', () => this.stopAutoplay());
        this.root.addEventListener('mouseleave', () => this.startAutoplay());

        this.setupSwipe();
    }

    buildDots() {
        this.dotsContainer.innerHTML = '';
        this.visibleSlides.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.className = 'work-carousel__dot';
            dot.type = 'button';
            dot.setAttribute('aria-label', `Показать слайд ${index + 1}`);
            dot.addEventListener('click', () => this.goTo(index));
            this.dotsContainer.appendChild(dot);
        });
    }

    updateDots() {
        Array.from(this.dotsContainer.children).forEach((dot, index) => {
            dot.classList.toggle('is-active', index === this.currentIndex);
        });
    }

    goTo(index) {
        if (this.visibleSlides.length === 0) return;
        this.currentIndex = (index + this.visibleSlides.length) % this.visibleSlides.length;
        const offset = -this.currentIndex * 100;
        this.track.style.transform = `translateX(${offset}%)`;
        this.updateDots();
        this.updateNav();
    }

    next() {
        this.goTo(this.currentIndex + 1);
    }

    prev() {
        this.goTo(this.currentIndex - 1);
    }

    updateNav() {
        const disabled = this.visibleSlides.length <= 1;
        if (this.prevBtn) this.prevBtn.disabled = disabled;
        if (this.nextBtn) this.nextBtn.disabled = disabled;
    }

    filterSlides(activeTab) {
        const category = activeTab.dataset.category;
        this.tabs.forEach((tab) => tab.classList.toggle('work-carousel__tab--active', tab === activeTab));

        this.visibleSlides = [];
        this.slides.forEach((slide) => {
            const matches = category === 'all' || slide.dataset.category === category;
            slide.style.display = matches ? '' : 'none';
            if (matches) this.visibleSlides.push(slide);
        });

        this.currentIndex = 0;
        this.buildDots();
        this.update();
        this.goTo(0);
        this.track.style.transform = 'translateX(0%)';
    }

    update() {
        this.visibleSlides.forEach((slide) => {
            slide.style.flex = '0 0 100%';
        });
        this.updateDots();
        this.updateNav();
    }

    setupSwipe() {
        let startX = null;
        this.track.addEventListener('touchstart', (event) => {
            startX = event.touches[0].clientX;
        });

        this.track.addEventListener('touchend', (event) => {
            if (startX === null) return;
            const diff = event.changedTouches[0].clientX - startX;
            if (Math.abs(diff) > 50) {
                diff < 0 ? this.next() : this.prev();
            }
            startX = null;
        });
    }

    startAutoplay() {
        if (this.visibleSlides.length <= 1) return;
        this.stopAutoplay();
        this.autoplayInterval = setInterval(() => this.next(), this.autoPlayDelay);
    }

    stopAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.work-carousel').forEach((section) => {
        new WorkCarousel(section);
    });
});
