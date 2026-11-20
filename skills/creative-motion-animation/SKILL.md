---
name: creative-motion-animation
description: High-end web animation and motion engineering using Framer Motion, GSAP (ScrollTrigger), and CSS spring physics (inspired by freshtechbro/claudedesignskills and Emil Kowalski design engineering). Eliminates stiff AI-generated linear transitions with natural spring physics, orchestrated stagger entrances, layout morphing (layoutId), micro-interactions, and reduced-motion accessibility.
---

# Creative Motion & Animation Engineering

A master skill for crafting fluid, production-grade animations and micro-interactions in modern web applications. Focuses on physical authenticity, purposeful motion choreography, and tactile responsiveness while avoiding generic, jarring "AI slop" animations.

## Core Philosophy of Motion

1. **Motion is Information, Not Decoration**: Every animation must communicate hierarchy, state transition, spatial orientation, or confirmation of intent.
2. **Never Use Linear Easing for Spatial Movement**: Real physical objects have inertia and mass. Always use calibrated spring physics or cubic-bezier curves with swift acceleration and soft deceleration.
3. **Respect User Autonomy**: Always honor `prefers-reduced-motion` to guarantee vestibular accessibility.
4. **Fast by Default**: Micro-interactions must feel instant (120ms - 220ms). Large page transitions should not exceed 350ms - 500ms.

---

## 1. Natural Spring Physics (Framer Motion)

Avoid duration-based tweens for interactive components; use calibrated spring constants:

```tsx
import { motion } from 'framer-motion';

// S-Tier Spring Presets for Tactile UI
export const SPRINGS = {
  // Snappy: Buttons, toggles, badges, dropdown items
  snappy: { type: 'spring', stiffness: 450, damping: 30, mass: 0.8 },

  // Gentle: Dialogs, sheets, expansive drawer panels
  gentle: { type: 'spring', stiffness: 260, damping: 26, mass: 1 },

  // Bouncy: Celebration icons, playful badges, gamified toasts
  bouncy: { type: 'spring', stiffness: 400, damping: 15, mass: 1 },

  // Stiff / Direct: Tooltips, cursor follower
  instant: { type: 'spring', stiffness: 600, damping: 40 }
};

export const TactileButton = ({ children, onClick }) => (
  <motion.button
    whileHover={{ scale: 1.025 }}
    whileTap={{ scale: 0.96 }}
    transition={SPRINGS.snappy}
    onClick={onClick}
    className="btn-primary"
  >
    {children}
  </motion.button>
);
```

---

## 2. Orchestrated Staggered Entrances

Never blast all content onto the screen at once. Orchestrate cascading reveals:

```tsx
export const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.1,
    }
  }
};

export const cardItemVariants = {
  hidden: { opacity: 0, y: 16, filter: 'blur(4px)' },
  visible: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 24
    }
  }
};
```

---

## 3. Seamless Layout Morphing (`layoutId`)

When expanding a card into a full modal, or sliding an active pill indicator between tabs:

```tsx
// Floating Active Tab Indicator
export const TabNav = ({ tabs, activeTab, setActiveTab }) => (
  <nav className="flex gap-2 p-1 bg-slate-900 rounded-xl relative">
    {tabs.map((tab) => {
      const isActive = activeTab === tab.id;
      return (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`relative px-4 py-2 text-sm z-10 transition-colors ${
            isActive ? 'text-white' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          {isActive && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute inset-0 bg-indigo-600 rounded-lg -z-10 shadow-lg shadow-indigo-500/20"
              transition={SPRINGS.snappy}
            />
          )}
          {tab.label}
        </button>
      );
    })}
  </nav>
);
```

---

## 4. Advanced GSAP & ScrollTrigger Pipelines

For rich editorial storytelling, parallax, pinned sections, and scrubbing:

```javascript
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function initHeroScrollStory() {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: '#hero-container',
      start: 'top top',
      end: '+=150%',
      scrub: 0.8,
      pin: true,
      anticipatePin: 1
    }
  });

  tl.to('.hero-title', { scale: 0.85, opacity: 0.4, y: -60 }, 0)
    .fromTo('.hero-3d-canvas', { scale: 1 }, { scale: 1.25, rotateY: 15 }, 0)
    .fromTo('.hero-bento-grid', { y: 200, opacity: 0 }, { y: 0, opacity: 1 }, 0.4);
}
```

---

## 5. Reduced-Motion Contract

Always provide a seamless CSS fallback:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
