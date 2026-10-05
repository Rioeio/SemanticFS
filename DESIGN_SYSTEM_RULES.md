# SemanticFS Design System Rules

This document establishes the canonical design system rules for SemanticFS frontend interfaces. Every screen, component, modal, and badge created or updated in this repository must strictly adhere to these rules.

---

## 1. Token Enforcement & Constraints

> [!IMPORTANT]
> **Zero Arbitrary Values Policy**
> - **Colors:** No arbitrary hex codes, OKLCH, or RGB values may be used anywhere in component code. Only values from `COLORS` and `EXT_COLORS` are permitted.
> - **Spacing:** Only values from the spacing scale (`4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`) are permitted for margins, paddings, and gaps.
> - **Typography:** Strictly use `'Inter'` for sans-serif text and `'JetBrains Mono'` for monospaced elements (code, tokens, scores, keyboard shortcuts, file extensions).

---

## 2. Canonical Color Palette

| Token | Hex Value | Role / Usage |
| :--- | :--- | :--- |
| `base` | `#16161D` | Application background, canvas root. |
| `surface` | `#1E1F29` | Cards, side panels, dropdowns, dialogs, modals. |
| `border` | `#2A2B38` | Element dividers, container borders, subtle outlines. |
| `textPrimary` | `#F2F1ED` | Main headings, primary content, query inputs, active items. |
| `textSecondary` | `#8B8D98` | Secondary labels, timestamps, metadata, placeholders, hints. |
| `accent` | `#9D7CFF` | Primary brand violet, active selection indicator, score chips. |
| `success` | `#7FBF6B` | Verified matches, healthy daemon status, active watchers. |
| `warning` | `#E6C265` | Stale index warnings, cautionary prompts, python badges. |
| `danger` | `#E5637A` | Error states, failed index jobs, delete folder triggers. |
| `highlight` | `#FF6FA8` | Query match highlights (`<mark>`), media/video icons. |
| `mono` | `#6FD3E8` | Monospace accents, code keywords, markdown badges. |

### File Type Badge Colors (`EXT_COLORS`)
- **Code & Markdown:** `md: #6FD3E8`, `ts: #6FD3E8`, `tsx: #9D7CFF`, `py: #E6C265`, `js: #E6C265`
- **Data & Config:** `json: #7FBF6B`, `csv: #7FBF6B`
- **Documents:** `pdf: #E5637A`, `txt: #8B8D98`
- **Media:** `png: #FF6FA8`, `jpg: #FF6FA8`, `mp4: #FF6FA8`
- **Archives / Directories:** `zip: #8B8D98`, `dir: #8B8D98`

---

## 3. Spacing Scale

Components must compose spacing exclusively from this scale:

| Level | Pixels | Common Usage |
| :--- | :--- | :--- |
| `SPACING[1]` | `4px` | Badge internal padding, chip gaps, divider margins. |
| `SPACING[2]` | `8px` | Icon-to-text gap, row vertical padding, chip spacing. |
| `SPACING[3]` | `12px` | Search input vertical padding, card inner gutter. |
| `SPACING[4]` | `16px` | Search input horizontal padding, container padding. |
| `SPACING[6]` | `24px` | Panel padding, section spacing. |
| `SPACING[8]` | `32px` | Large section dividers, header margins. |
| `SPACING[12]` | `48px` | Empty state padding, modal top offset. |

---

## 4. Typography Scale

- **Sans Font Family:** `'Inter', system-ui, -apple-system, sans-serif`
- **Mono Font Family:** `'JetBrains Mono', monospace`

| Level | Size | Weight | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- |
| `xs` | `12px` | 400 / 500 / 600 | `16px` | Score chips, kbd badges, status metadata, citations. |
| `sm` | `14px` | 400 / 500 | `20px` | Snippets, secondary descriptions, list item text. |
| `md` | `16px` | 400 / 500 / 600 | `24px` | File names, search input text, standard body. |
| `lg` | `20px` | 600 | `28px` | Panel titles, modal section headers. |
| `xl` | `28px` | 600 | `36px` | Main screen titles, hero headers. |

---

## 5. Border Radius Scale

- `sm` (`4px`): Badges, score chips, keyboard shortcuts (`<kbd>`), small buttons.
- `md` (`6px`): Result rows, input containers, code block containers.
- `lg` (`10px`): Main modal containers, flyout drawers, status panels.

---

## 6. Keyboard & Interaction Patterns

1. **Global Search Activation:** Pressing `/` anywhere on the screen must focus the search input unless another input is currently active.
2. **Result Traversal:** `ArrowDown` (`↓`) and `ArrowUp` (`↑`) move the active result selection cleanly.
3. **Execution:** Pressing `Enter` (`↵`) on a selected result opens the file preview or launches the target file.
4. **Escape Dismissal:** Pressing `Escape` clears the active search query, deselects the current item, or closes open slide-over panels.
5. **Status Panel Toggle:** `Cmd+,` (macOS) or `Ctrl+,` (Windows/Linux) toggles the settings & daemon status panel.

---

## 7. Fidelity Verification Checklist

Before accepting any screen implementation:
- [ ] No inline hex codes outside `COLORS` or `EXT_COLORS`.
- [ ] Borders use `#2A2B38` at `1px`.
- [ ] Query highlight marks use `#FF6FA8` with `~0.15–0.25` alpha background and full `#FF6FA8` foreground.
- [ ] Keyboard hints in footer use styled `<kbd>` tags with mono font and subtle border.
