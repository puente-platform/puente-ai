"use client";

import React, { useRef, useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import avatarMarcus from "@/assets/avatar-marcus.jpg";
import avatarElena from "@/assets/avatar-elena.jpg";
import avatarErnesto from "@/assets/avatar-ernesto.jpg";
import avatarMontse from "@/assets/avatar-montse.jpg";
import avatarJavier from "@/assets/avatar-javier.jpg";
import avatarSofia from "@/assets/avatar-sofia.jpg";
import avatarManuel from "@/assets/avatar-manuel.jpg";
import avatarThiago from "@/assets/avatar-thiago.jpg";
import avatarBeatriz from "@/assets/avatar-beatriz.jpg";
import avatarFelipe from "@/assets/avatar-felipe.jpg";
import avatarIsaac from "@/assets/avatar-isaac.jpg";
import avatarMiriam from "@/assets/avatar-miriam.jpg";
import avatarDavid from "@/assets/avatar-david.jpg";
import avatarSamuel from "@/assets/avatar-samuel.jpg";
import avatarRachel from "@/assets/avatar-rachel.jpg";
import avatarAvi from "@/assets/avatar-avi.jpg";

export default function TestimonialsBackgroundWithDrag() {
  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-background">
      <TestimonialsCanvas>
        <div className="relative z-10 flex flex-col items-center justify-center px-4">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-4xl md:text-6xl font-bold font-display text-foreground leading-tight">
              Loved by thousands{" "}
              <br className="hidden md:block" />
              of happy customers
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-xl mx-auto">
              Hear from our community of builders, designers, and creators who
              trust us to power their projects.
            </p>
            <a
              href="#"
              className="mt-6 inline-flex items-center gap-2 text-primary hover:underline font-medium"
            >
              Read all reviews
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </a>
          </div>
        </div>
      </TestimonialsCanvas>
    </div>
  );
}

// Default testimonials data
const DEFAULT_TESTIMONIALS: Testimonial[] = [
  {
    title: "Saved $740 on the very first invoice",
    quote:
      "We were losing nearly $800 on every single wire to Brazil through our traditional bank. I thought that was just the 'cost of doing business.' Puente AI showed us a route that saved us $740 on the very first invoice. It paid for itself in seconds.",
    imageSrc: avatarMarcus,
    name: "Marcus T., Electronics Importer (Miami, FL)",
  },
  {
    title: "The institutional security we were missing",
    quote:
      "The 'Three Answers' feature is a lifesaver. Before Puente, I'd hold my breath for three days waiting for a supplier to confirm receipt. Now, I know the fraud risk and the compliance status before I even hit 'send.' It's the institutional security we were missing.",
    imageSrc: avatarElena,
    name: "Elena R., Logistics Coordinator",
  },
  {
    title: "Turns a high-stress gamble into a 15-second certainty",
    quote:
      "I've literally stood in a warehouse parking lot in 95-degree heat, trying to wire $50,000 to a supplier in Honduras on a glitchy banking app. I was sweating—not just from the heat, but from the fear of a typo or a fraudster. Puente AI was built for that exact moment. It turns a high-stress gamble into a 15-second certainty.",
    imageSrc: avatarErnesto,
    name: "Ernesto S., Founder",
  },
  {
    title: "La seguridad institucional que nos faltaba",
    quote:
      "La función de 'Tres Respuestas' es vital. Antes de Puente, pasaba tres días conteniendo el aliento esperando que el proveedor confirmara el pago. Ahora, conozco el riesgo de fraude y el estado de cumplimiento antes de disparar el pago. Es la seguridad institucional que nos faltaba.",
    imageSrc: avatarMontse,
    name: "Montse R., Coordinadora de Logística",
  },
  {
    title: "Ese dinero se queda en nuestra expansión",
    quote:
      "Solíamos aceptar las comisiones bancarias como un mal necesario. Con Puente AI, descubrimos que estábamos regalando casi $934 en cada envío a Bogotá. Ahora, ese dinero se queda en nuestra expansión.",
    imageSrc: avatarJavier,
    name: "Javier M., Importador de Textiles (Medellín/Miami)",
  },
  {
    title: "Un guardaespaldas financiero",
    quote:
      "El mercado de proveedores en LATAM suele ser tenaz. La puntuación de fraude de Puente nos salvó de enviar $30,000 a una cuenta fantasma. Es como tener un guardaespaldas financiero.",
    imageSrc: avatarSofia,
    name: "Sofia G., Dueña de Distribuidora (Doral, FL)",
  },
  {
    title: "Eficiencia pura",
    quote:
      "Lo que antes tomaba mañanas enteras de llamadas al banco y hojas de cálculo, ahora se resuelve en 15 segundos. Subes la factura y tienes la respuesta. Es eficiencia pura.",
    imageSrc: avatarManuel,
    name: "Manuel Z., Gerente de Logística",
  },
  {
    title: "O sistema se pagou em segundos",
    quote:
      "Perdíamos quase $800 em cada remessa para o Brasil. Com a Puente AI, economizamos $740 logo na primeira fatura. O sistema se pagou em segundos e mudou nossa margem de lucro.",
    imageSrc: avatarThiago,
    name: "Thiago S., Importador de Eletrônicos (São Paulo/Miami)",
  },
  {
    title: "Opero com total confiança",
    quote:
      "A segurança é tudo. Antes da Puente, eu ficava apreensiva a cada novo fornecedor. Agora, com a análise de fraude e compliance em tempo real, opero com total confiança.",
    imageSrc: avatarBeatriz,
    name: "Beatriz L., Coordenadora de Operações",
  },
  {
    title: "Indispensável",
    quote:
      "A história do estacionamento é real. Eu já estive lá, suando frio tentando fechar um câmbio. A Puente AI transforma esse caos em uma certeza de 15 segundos. É indispensável.",
    imageSrc: avatarFelipe,
    name: "Felipe R., Empreendedor",
  },
  {
    title: "La tranquilidad que mi negocio exige",
    quote:
      "Importar productos Kosher desde Argentina requiere una precisión absoluta en el cumplimiento. Con Puente AI, validamos proveedores y rutas de pago en 15 segundos. Es la tranquilidad que mi negocio y mi comunidad exigen.",
    imageSrc: avatarIsaac,
    name: "Isaac B., Importador de Alimentos (Aventura, FL)",
  },
  {
    title: "Precios competitivos sin sacrificar calidad",
    quote:
      "En nuestra comunidad, la palabra es sagrada, pero los bancos no perdonan. Ahorrar $840 en cada transferencia a Panamá nos permite mantener precios competitivos sin sacrificar la calidad que nuestros clientes esperan.",
    imageSrc: avatarMiriam,
    name: "Miriam L., Propietaria de Boutique (Miami Beach)",
  },
  {
    title: "Nuestra herramienta de confianza",
    quote:
      "Durante las festividades, el volumen de importación es masivo. Puente AI nos permite escanear facturas y asegurar que los fondos lleguen a tiempo y de forma segura. Se ha convertido en nuestra herramienta de confianza.",
    imageSrc: avatarDavid,
    name: "David S., Distribuidor de Artículos Especializados",
  },
  {
    title: "Segurança institucional com agilidade de startup",
    quote:
      "Trazer produtos especializados para a comunidade em São Paulo e Miami ficou muito mais simples. A Puente AI faz o compliance e a verificação de fraude instantaneamente. Segurança institucional com agilidade de startup.",
    imageSrc: avatarSamuel,
    name: "Samuel K., Importador de Eletrônicos (Hebraica, SP)",
  },
  {
    title: "Revolucionária para nós",
    quote:
      "Economizar no câmbio em remessas internacionais significa investir mais na nossa congregação e no nosso estoque. A transparência da Puente AI em mostrar as taxas ocultas dos bancos é revolucionária para nós.",
    imageSrc: avatarRachel,
    name: "Rachel G., Gestora de Logística Internacional",
  },
  {
    title: "Essencial para nossa paz de espírito",
    quote:
      "Confiança é a base de tudo o que fazemos. Saber que o fornecedor é legítimo e que estamos na rota de pagamento mais eficiente antes de apertar o 'enviar' é essencial para nossa paz de espírito.",
    imageSrc: avatarAvi,
    name: "Avi M., Diretor Comercial",
  },
];

interface Testimonial {
  title: string;
  quote: string;
  imageSrc: string;
  name: string;
}

interface TestimonialCardItem {
  id: string;
  testimonial: Testimonial;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
}

function seededRandom(seed: number): () => number {
  return function () {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
}

function rectanglesOverlap(
  x1: number, y1: number, w1: number, h1: number,
  x2: number, y2: number, w2: number, h2: number,
  padding: number = 20,
): boolean {
  return !(
    x1 + w1 + padding < x2 ||
    x2 + w2 + padding < x1 ||
    y1 + h1 + padding < y2 ||
    y2 + h2 + padding < y1
  );
}

function isInWorldCenterZone(
  absoluteX: number, absoluteY: number,
  width: number, height: number,
  exclusionWidth: number, exclusionHeight: number,
): boolean {
  const zoneLeft = -exclusionWidth / 2;
  const zoneRight = exclusionWidth / 2;
  const zoneTop = -exclusionHeight / 2;
  const zoneBottom = exclusionHeight / 2;
  const cardRight = absoluteX + width;
  const cardBottom = absoluteY + height;
  return !(
    cardRight < zoneLeft ||
    absoluteX > zoneRight ||
    cardBottom < zoneTop ||
    absoluteY > zoneBottom
  );
}

function generateTileCards(
  tileX: number, tileY: number, tileSize: number,
  testimonials: Testimonial[], cardCount: number = 4,
  exclusionWidth: number = 700, exclusionHeight: number = 600,
  randomRotate: boolean = false,
): TestimonialCardItem[] {
  const seed = tileX * 10000 + tileY;
  const random = seededRandom(seed);
  const cards: TestimonialCardItem[] = [];
  const maxAttempts = 100;
  const minGap = 80;

  for (let i = 0; i < cardCount; i++) {
    const testimonialIndex =
      Math.abs(tileX * cardCount + tileY + i) % testimonials.length;
    const baseWidth = 380 + random() * 60;
    const height = 200 + random() * 30;
    let x = 0, y = 0, attempts = 0, validPosition = false;

    while (attempts < maxAttempts && !validPosition) {
      x = random() * (tileSize - baseWidth - 80) + 40;
      y = random() * (tileSize - height - 80) + 40;
      const absoluteX = tileX * tileSize + x;
      const absoluteY = tileY * tileSize + y;

      if (isInWorldCenterZone(absoluteX, absoluteY, baseWidth, height, exclusionWidth, exclusionHeight)) {
        attempts++;
        continue;
      }

      validPosition = true;
      for (const existingCard of cards) {
        if (rectanglesOverlap(x, y, baseWidth, height, existingCard.x, existingCard.y, existingCard.width, existingCard.height, minGap)) {
          validPosition = false;
          break;
        }
      }
      attempts++;
    }

    if (validPosition) {
      const rotation = randomRotate ? random() * 16 - 8 : 0;
      cards.push({
        id: `${tileX}-${tileY}-${i}`,
        testimonial: testimonials[testimonialIndex],
        x, y, width: baseWidth, height, rotation,
      });
    }
  }
  return cards;
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

interface FocusPosition {
  x: number; y: number;
  cardWidth: number; cardHeight: number; cardId: string;
}

function generateFocusPositions(
  count: number, tileSize: number, testimonials: Testimonial[],
  cardsPerTile: number, exclusionWidth: number, exclusionHeight: number,
): FocusPosition[] {
  const positions: FocusPosition[] = [];
  const tileRange = 3;
  for (let tx = -tileRange; tx <= tileRange && positions.length < count; tx++) {
    for (let ty = -tileRange; ty <= tileRange && positions.length < count; ty++) {
      if (tx === 0 && ty === 0) continue;
      const cards = generateTileCards(tx, ty, tileSize, testimonials, cardsPerTile, exclusionWidth, exclusionHeight, false);
      if (cards.length > 0) {
        const card = cards[0];
        const absoluteX = tx * tileSize + card.x;
        const absoluteY = ty * tileSize + card.y;
        positions.push({
          x: absoluteX + card.width / 2,
          y: absoluteY + card.height / 2,
          cardWidth: card.width, cardHeight: card.height, cardId: card.id,
        });
      }
    }
  }
  return positions;
}

interface TestimonialsCanvasProps {
  testimonials?: Testimonial[];
  tileSize?: number;
  cardsPerTile?: number;
  className?: string;
  children?: React.ReactNode;
  centerExclusionWidth?: number;
  centerExclusionHeight?: number;
  randomRotate?: boolean;
  autoPanInterval?: number;
  autoPanDuration?: number;
}

export function TestimonialsCanvas({
  testimonials = DEFAULT_TESTIMONIALS,
  tileSize = 800,
  cardsPerTile = 4,
  className,
  children,
  centerExclusionWidth = 700,
  centerExclusionHeight = 600,
  randomRotate = false,
  autoPanInterval = 3000,
  autoPanDuration = 1200,
}: TestimonialsCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const offsetRef = useRef({ x: 0, y: 0 });
  const velocityRef = useRef({ x: 0, y: 0 });
  const isDraggingRef = useRef(false);
  const lastPosRef = useRef({ x: 0, y: 0 });
  const lastTimeRef = useRef(Date.now());
  const rafRef = useRef<number | null>(null);

  const autoPanRafRef = useRef<number | null>(null);
  const autoPanTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isAutoPanningRef = useRef(false);
  const focusIndexRef = useRef(0);
  const focusPositionsRef = useRef<FocusPosition[]>([]);

  const [isDragging, setIsDragging] = useState(false);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [visibleTiles, setVisibleTiles] = useState<
    { tileX: number; tileY: number; cards: TestimonialCardItem[] }[]
  >([]);

  const updateVisibleTiles = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;
    const { width, height } = container.getBoundingClientRect();
    const { x, y } = offsetRef.current;
    const buffer = 1;
    const startTileX = Math.floor(x / tileSize) - buffer;
    const startTileY = Math.floor(y / tileSize) - buffer;
    const endTileX = Math.ceil((x + width) / tileSize) + buffer;
    const endTileY = Math.ceil((y + height) / tileSize) + buffer;
    const tiles: { tileX: number; tileY: number; cards: TestimonialCardItem[] }[] = [];
    for (let tx = startTileX; tx <= endTileX; tx++) {
      for (let ty = startTileY; ty <= endTileY; ty++) {
        tiles.push({
          tileX: tx, tileY: ty,
          cards: generateTileCards(tx, ty, tileSize, testimonials, cardsPerTile, centerExclusionWidth, centerExclusionHeight, randomRotate),
        });
      }
    }
    setVisibleTiles(tiles);
  }, [tileSize, testimonials, cardsPerTile, centerExclusionWidth, centerExclusionHeight, randomRotate]);

  const updateTransform = useCallback(() => {
    if (contentRef.current) {
      const { x, y } = offsetRef.current;
      contentRef.current.style.transform = `translate3d(${-x}px, ${-y}px, 0)`;
    }
  }, []);

  const animate = useCallback(() => {
    if (isDraggingRef.current) {
      rafRef.current = requestAnimationFrame(animate);
      return;
    }
    const friction = 0.95;
    const minVelocity = 0.5;
    velocityRef.current.x *= friction;
    velocityRef.current.y *= friction;
    if (Math.abs(velocityRef.current.x) > minVelocity || Math.abs(velocityRef.current.y) > minVelocity) {
      offsetRef.current.x -= velocityRef.current.x;
      offsetRef.current.y -= velocityRef.current.y;
      updateTransform();
      updateVisibleTiles();
      rafRef.current = requestAnimationFrame(animate);
    } else {
      velocityRef.current = { x: 0, y: 0 };
    }
  }, [updateTransform, updateVisibleTiles]);

  const panToNextTestimonial = useCallback(() => {
    if (isDraggingRef.current || isAutoPanningRef.current) return;
    const container = containerRef.current;
    if (!container || focusPositionsRef.current.length === 0) return;
    const { width, height } = container.getBoundingClientRect();
    focusIndexRef.current = (focusIndexRef.current + 1) % focusPositionsRef.current.length;
    const target = focusPositionsRef.current[focusIndexRef.current];
    const targetX = target.x - width / 2;
    const targetY = target.y - height / 2 + 280;
    const startX = offsetRef.current.x;
    const startY = offsetRef.current.y;
    const deltaX = targetX - startX;
    const deltaY = targetY - startY;
    const startTime = performance.now();
    isAutoPanningRef.current = true;

    const animateAutoPan = (currentTime: number) => {
      if (isDraggingRef.current) {
        isAutoPanningRef.current = false;
        setActiveCardId(null);
        return;
      }
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / autoPanDuration, 1);
      const easedProgress = easeOutCubic(progress);
      offsetRef.current.x = startX + deltaX * easedProgress;
      offsetRef.current.y = startY + deltaY * easedProgress;
      updateTransform();
      updateVisibleTiles();
      if (progress < 1) {
        autoPanRafRef.current = requestAnimationFrame(animateAutoPan);
      } else {
        isAutoPanningRef.current = false;
        setActiveCardId(target.cardId);
        if (!isDraggingRef.current) {
          autoPanTimerRef.current = setTimeout(panToNextTestimonial, autoPanInterval);
        }
      }
    };
    autoPanRafRef.current = requestAnimationFrame(animateAutoPan);
  }, [autoPanDuration, autoPanInterval, updateTransform, updateVisibleTiles]);

  const startAutoPan = useCallback(() => {
    if (autoPanTimerRef.current) clearTimeout(autoPanTimerRef.current);
    autoPanTimerRef.current = setTimeout(panToNextTestimonial, autoPanInterval);
  }, [autoPanInterval, panToNextTestimonial]);

  const stopAutoPan = useCallback(() => {
    if (autoPanTimerRef.current) { clearTimeout(autoPanTimerRef.current); autoPanTimerRef.current = null; }
    if (autoPanRafRef.current) { cancelAnimationFrame(autoPanRafRef.current); autoPanRafRef.current = null; }
    isAutoPanningRef.current = false;
    setActiveCardId(null);
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    isDraggingRef.current = true;
    setIsDragging(true);
    lastPosRef.current = { x: e.clientX, y: e.clientY };
    lastTimeRef.current = Date.now();
    velocityRef.current = { x: 0, y: 0 };
    stopAutoPan();
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
  }, [stopAutoPan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    const dx = e.clientX - lastPosRef.current.x;
    const dy = e.clientY - lastPosRef.current.y;
    const now = Date.now();
    const dt = now - lastTimeRef.current;
    if (dt > 0) {
      velocityRef.current.x = (dx / dt) * 16;
      velocityRef.current.y = (dy / dt) * 16;
    }
    offsetRef.current.x -= dx;
    offsetRef.current.y -= dy;
    lastPosRef.current = { x: e.clientX, y: e.clientY };
    lastTimeRef.current = now;
    updateTransform();
    updateVisibleTiles();
  }, [updateTransform, updateVisibleTiles]);

  const handleMouseUp = useCallback(() => {
    if (!isDraggingRef.current) return;
    isDraggingRef.current = false;
    setIsDragging(false);
    rafRef.current = requestAnimationFrame(animate);
    startAutoPan();
  }, [animate, startAutoPan]);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    isDraggingRef.current = true;
    setIsDragging(true);
    lastPosRef.current = { x: touch.clientX, y: touch.clientY };
    lastTimeRef.current = Date.now();
    velocityRef.current = { x: 0, y: 0 };
    stopAutoPan();
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
  }, [stopAutoPan]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!isDraggingRef.current) return;
    e.preventDefault();
    const touch = e.touches[0];
    const dx = touch.clientX - lastPosRef.current.x;
    const dy = touch.clientY - lastPosRef.current.y;
    const now = Date.now();
    const dt = now - lastTimeRef.current;
    if (dt > 0) {
      velocityRef.current.x = (dx / dt) * 16;
      velocityRef.current.y = (dy / dt) * 16;
    }
    offsetRef.current.x -= dx;
    offsetRef.current.y -= dy;
    lastPosRef.current = { x: touch.clientX, y: touch.clientY };
    lastTimeRef.current = now;
    updateTransform();
    updateVisibleTiles();
  }, [updateTransform, updateVisibleTiles]);

  const handleTouchEnd = useCallback(() => {
    if (!isDraggingRef.current) return;
    isDraggingRef.current = false;
    setIsDragging(false);
    rafRef.current = requestAnimationFrame(animate);
    startAutoPan();
  }, [animate, startAutoPan]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const { width, height } = container.getBoundingClientRect();
    offsetRef.current = { x: -width / 2, y: -height / 2 };
    focusPositionsRef.current = generateFocusPositions(16, tileSize, testimonials, cardsPerTile, centerExclusionWidth, centerExclusionHeight);
    updateVisibleTiles();
    updateTransform();
    const initialTimer = setTimeout(() => { startAutoPan(); }, autoPanInterval);
    return () => {
      clearTimeout(initialTimer);
      stopAutoPan();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [updateVisibleTiles, updateTransform, tileSize, testimonials, cardsPerTile, centerExclusionWidth, centerExclusionHeight, autoPanInterval, startAutoPan, stopAutoPan]);

  useEffect(() => {
    const handleResize = () => updateVisibleTiles();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [updateVisibleTiles]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative w-full h-screen overflow-hidden",
        isDragging ? "cursor-grabbing" : "cursor-grab",
        className,
      )}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Dot grid background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle, hsl(var(--muted-foreground) / 0.15) 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
      />

      {/* Scrollable content layer */}
      <div
        ref={contentRef}
        className="absolute top-0 left-0"
        style={{ willChange: "transform" }}
      >
        {visibleTiles.map((tile) => (
          <div
            key={`${tile.tileX}-${tile.tileY}`}
            className="absolute"
            style={{
              left: tile.tileX * tileSize,
              top: tile.tileY * tileSize,
              width: tileSize,
              height: tileSize,
            }}
          >
            {tile.cards.map((card) => {
              const isActive = activeCardId === card.id;
              const hasActiveCard = activeCardId !== null;
              return (
                <motion.div
                  key={card.id}
                  className="absolute select-none"
                  style={{
                    left: card.x,
                    top: card.y,
                    width: card.width,
                    height: card.height,
                    rotate: card.rotation,
                  }}
                  animate={{
                    scale: isActive ? 1.05 : 1,
                    opacity: hasActiveCard ? (isActive ? 1 : 0.4) : 0.85,
                  }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                >
                  {/* Testimonial content */}
                  <div
                    className={cn(
                      "w-full h-full rounded-xl border bg-card p-5 shadow-sm transition-shadow duration-300",
                      isActive && "shadow-lg ring-2 ring-primary/20",
                    )}
                  >
                    <div className="flex flex-col justify-between h-full">
                      <div>
                        <p className="text-sm font-semibold text-foreground leading-snug">
                          &ldquo;{card.testimonial.title}&rdquo;
                        </p>
                        <p className="mt-2 text-xs text-muted-foreground leading-relaxed line-clamp-4">
                          {card.testimonial.quote}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 mt-3">
                        <img
                          src={card.testimonial.imageSrc}
                          alt={card.testimonial.name}
                          className="w-7 h-7 rounded-full object-cover"
                        />
                        <span className="text-xs font-medium text-foreground">
                          {card.testimonial.name}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Children overlay */}
      {children && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="pointer-events-auto">{children}</div>
        </div>
      )}
    </div>
  );
}
