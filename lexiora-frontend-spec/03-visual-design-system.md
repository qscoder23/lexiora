# 03. Visual Design System

## Design direction

The UI should look like a premium B2B knowledge product for legal work.

Keywords:
- restrained
- elegant
- sharp
- high-trust
- fluid
- minimal
- text-centric
- dark-accented neutrals

Reference feel:
- premium document tools
- modern research products
- high-end analytics software
- not flashy, not gamer, not “AI toy”

## Color system

Use a **warm-neutral base** with a **deep navy accent** and a restrained teal/indigo highlight for intelligence and graph states.

### Core palette
- Background: `#F6F4EF`
- Surface: `#FFFCF8`
- Elevated surface: `#FFFFFF`
- Border subtle: `#E5DED2`
- Border strong: `#CFC4B2`
- Text primary: `#171717`
- Text secondary: `#5F5A52`
- Text tertiary: `#8C857A`
- Primary accent: `#16263F`
- Primary accent hover: `#1D3252`
- Secondary accent: `#2A6F6B`
- Secondary accent soft: `#DDF1EE`
- Info: `#4069D8`
- Success: `#257A52`
- Warning: `#A36A16`
- Danger: `#A33B3B`
- Danger soft: `#FBEAEA`
- Citation highlight: `#EEF3FF`
- Graph node soft: `#E8F0EE`

## Dark mode (optional)
If implemented, it should be true premium dark mode, not inverted cream mode.

Suggested:
- Background: `#0F1217`
- Surface: `#141922`
- Elevated: `#1A2130`
- Border: `#2A3446`
- Text primary: `#F4F6FA`
- Text secondary: `#ADB7C8`
- Accent: `#90AFFF`

## Typography

Prefer the following stack:
- Inter for UI and body
- IBM Plex Serif or Source Serif for selected legal document headings / quotations

### Type scale
- Display: 40 / 48 / semibold
- H1: 32 / 40 / semibold
- H2: 24 / 32 / semibold
- H3: 20 / 28 / semibold
- Body large: 16 / 28 / regular
- Body: 15 / 24 / regular
- Body small: 14 / 20 / regular
- Meta: 12 / 16 / medium
- Mono: 12 / 18 / medium

### Typography rules
- Keep line length readable for long legal text.
- Use stronger hierarchy than color changes.
- Avoid all-caps except tiny metadata labels.

## Radius
- Small: 8px
- Medium: 12px
- Large: 16px
- XL panel / modal: 20px
- Pill: 999px

## Shadows
Very subtle only.
- Sm: `0 1px 2px rgba(16,24,40,0.04)`
- Md: `0 8px 24px rgba(16,24,40,0.06)`
- Lg: `0 16px 40px rgba(16,24,40,0.08)`

## Spacing scale
- 4, 8, 12, 16, 20, 24, 32, 40, 48, 64

## Layout grid
- Max content width: 1440px
- Shell padding: 24px desktop, 16px tablet
- Panel gap: 16px to 20px

## Motion
Motion should feel smooth and precise.

### Rules
- Use ease-out or spring for drawer/panel transitions
- Duration: 140ms to 220ms for most UI motion
- Hover transitions: 120ms
- Streaming answer appearance: subtle fade + translateY 4px
- Avoid oversized motion or playful bounce

## Component styling language

### Buttons
- solid primary for key actions
- subtle secondary for low-emphasis actions
- ghost button for inline controls
- destructive button only in narrow contexts

### Cards
- soft border
- clean surface
- slightly elevated on hover only if interactive

### Inputs
- large comfortable height
- warm neutral fill or white background
- stronger focus ring in accent tone

### Tags and badges
Need strong semantic distinction:
- law
- case
- evidence
- agent active
- draft
- verified
- high risk

## Accessibility requirements
- WCAG AA contrast minimum
- visible keyboard focus states
- reduced motion support
- all icon-only controls require tooltip and aria-label
- streaming content should not break screen reader flow

## Iconography
Use a crisp, modern outline icon set such as Lucide.
Avoid decorative icons in dense legal content areas.

## Visual anti-patterns
Do not use:
- neon gradients
- glassmorphism
- excessive blur
- oversized shadows
- bright saturated AI-style glows
- mascot illustrations
