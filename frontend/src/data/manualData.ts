import { ManualEntry } from '../types/manual';

export const manualDatabase: ManualEntry[] = [
  {
    id: "RTG-MK1",
    title: "Multi-Mission Radioisotope Thermoelectric Generator (MMRTG)",
    category: "Power",
    access_level: 1,
    technical_content: {
      schematic_url: "/assets/schematics/rtg_core.png",
      specs: `
**Thermal Output**: 2000 Wt
**Electrical Output**: 110 We (Initial BOL)
**Fuel Source**: Plutonium-238 (PuO2)
**Half-Life**: 87.7 Years
**Housing Temp**: >200°C (Surface)
**Dimensions**: 64cm x 66cm (Fin-to-Fin)
      `.trim(),
      warnings: [
        "EXTREME THERMAL HAZARD: Do NOT touch cooling fins without thermal protection.",
        "RADIATION HAZARD: In case of housing breach, evacuate sector immediately.",
        "DO NOT SUBMERGE in potable water supply."
      ],
      formulas: [
        "P(t) = P0 * (1/2)^(t/87.7)",
        "Q = mcΔT (Thermal Transfer)"
      ]
    },
    lore_snippet: "Note: Who was the genius that decided to bury this thing 4km away? If the hab heating fails, I swear I'm digging it up and spooning with it. — Commander Lewis"
  },
  {
    id: "CO2-SCRUB-MK4",
    title: "Atmospheric Regulator: CO2 Scrubber Assembly",
    category: "LifeSupport",
    access_level: 1,
    technical_content: {
      schematic_url: "/assets/schematics/co2_scrubber.png",
      specs: `
**Flow Rate**: 15 CFM (Nominal)
**Filter Media**: Lithium Hydroxide (LiOH) Canisters
**Reaction Type**: Exothermic Absorption
**Capacity**: 4 Crew / 24 Hours per Canister
**Operating Temp**: 15°C - 35°C
      `.trim(),
      warnings: [
        "CAUTION: LiOH dust is highly corrosive to mucous membranes.",
        "DANGER: Do not bypass pre-filter assembly.",
        "CRITICAL: Saturation indicated by purple discoloration of indicator strip."
      ],
      formulas: [
        "2LiOH(s) + CO2(g) -> Li2CO3(s) + H2O(g) + Q",
        "Reaction Enthalpy: -89.6 kJ/mol"
      ]
    },
    lore_snippet: "Maintenance Log: The 'Universal' adapter ring is missing from the spare parts kit. If the main unit fails, we'll have to improvise connections for the square filters. Good luck. — Engineering Chief O'Neal"
  },
  {
    id: "PDU-ALPHA",
    title: "Primary Power Distribution Unit (PDU)",
    category: "Power",
    access_level: 0,
    technical_content: {
        schematic_url: "svg-internal", // Special flag for the SVG component
        specs: `
**Input Voltage**: 120V DC
**Max Load**: 50A
**Circuit Breaker**: Thermal-Magnetic
**Terminals**: A(+) / B(-) / G(GND)
        `.trim(),
        warnings: [
            "Disconnect main bus before servicing.",
            "Cross-wiring terminals A and B results in immediate fuse blowout."
        ],
        formulas: ["V = IR", "P = VI"]
    },
    lore_snippet: "It buzzes. It always buzzes. Even when I turn it off, I can still hear it in my dreams."
  }
];
