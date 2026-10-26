document.addEventListener('DOMContentLoaded', () => {

    const prefereMenosMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefereMenosMovimento) {
        return; 
    }


    /* ================================
       1. Parallax nos círculos decorativos
    ================================= */
    const circles = document.querySelectorAll('.circle');
    let mouseX = 0, mouseY = 0;
    let alvoX = 0, alvoY = 0;

    window.addEventListener('mousemove', (e) => {
        alvoX = (e.clientX / window.innerWidth) - 0.5;
        alvoY = (e.clientY / window.innerHeight) - 0.5;
    });

    function animarParallax() {
        mouseX += (alvoX - mouseX) * 0.06;
        mouseY += (alvoY - mouseY) * 0.06;

        circles.forEach((circle, index) => {
            const speed = (index + 1) * 25;
            circle.style.transform = `translate(${mouseX * speed}px, ${mouseY * speed}px)`;
        });

        requestAnimationFrame(animarParallax);
    }

    if (circles.length && !('ontouchstart' in window)) {
        requestAnimationFrame(animarParallax);
    }

    const titulo = document.querySelector('h1');

    function agendarGlitch() {
        const proximoGlitch = 3000 + Math.random() * 4000; // entre 3s e 7s

        setTimeout(() => {
            if (titulo) {
                titulo.classList.add('glitch');
                setTimeout(() => titulo.classList.remove('glitch'), 250);
            }
            agendarGlitch();
        }, proximoGlitch);
    }

    if (titulo) {
        agendarGlitch();
    }

    /* ================================
       3. Partículas flutuantes no fundo
    ================================= */
    const ehMobile = window.innerWidth < 600;
    const totalParticulas = ehMobile ? 12 : 25;
    const fragmento = document.createDocumentFragment();

    for (let i = 0; i < totalParticulas; i++) {
        const particula = document.createElement('span');
        particula.className = 'particula';

        const tamanho = Math.random() * 9 + 2;
        const posX = Math.random() * 100;
        const duracao = Math.random() * 10 + 8;
        const atraso = Math.random() * 10;
        const opacidade = (Math.random() * 0.4 + 0.3).toFixed(2);

        particula.style.width = `${tamanho}px`;
        particula.style.height = `${tamanho}px`;
        particula.style.left = `${posX}vw`;
        particula.style.animationDuration = `${duracao}s`;
        particula.style.animationDelay = `${atraso}s`;
        particula.style.setProperty('--opacidade-max', opacidade);

        fragmento.appendChild(particula);
    }

    document.body.appendChild(fragmento);


    /* ================================
       4. Botão com pulso ao carregar
    ================================= */
    const botao = document.querySelector('.btn');
    if (botao) {
        setTimeout(() => {
            botao.classList.add('pulso');
            botao.addEventListener('animationend', () => {
                botao.classList.remove('pulso');
            }, { once: true });
        }, 1200);
    }


    /* ================================
       5. Entrada escalonada (logo → card → footer)
       em vez de tudo aparecer junto
    ================================= */
    const elementosEntrada = [
        document.querySelector('.logo'),
        document.querySelector('.container'),
        document.querySelector('footer')
    ].filter(Boolean);

    elementosEntrada.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.animation = `fade 0.7s ease forwards`;
        el.style.animationDelay = `${i * 0.15}s`;
    });

});