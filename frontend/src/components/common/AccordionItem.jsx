import { useState } from 'react';

/**
 * AccordionItem — collapsible item matching the existing improvement-item style.
 *
 * Props:
 *  - header    {ReactNode}  always-visible header content
 *  - children  {ReactNode}  collapsible body
 *  - defaultOpen {boolean}  first item open by default
 *  - priorityBadge {ReactNode}  optional badge rendered in the header-right
 */
export default function AccordionItem({
  header,
  children,
  defaultOpen = false,
  priorityBadge = null,
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`improvement-item${open ? ' active' : ''}`}>
      <div
        className="improvement-header"
        onClick={() => setOpen((o) => !o)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setOpen((o) => !o)}
        aria-expanded={open}
      >
        <div className="improvement-header-left">
          {header}
        </div>
        <div className="improvement-header-right">
          {priorityBadge}
          <div className="accordion-icon">▼</div>
        </div>
      </div>
      <div className="improvement-content">
        {children}
      </div>
    </div>
  );
}
