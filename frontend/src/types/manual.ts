export type Category = "LifeSupport" | "Power" | "Rover" | "Comms" | "Emergency";

export interface TechnicalContent {
  schematic_url?: string;
  specs: string; // Markdown formatted string
  warnings: string[];
  formulas: string[];
}

export interface ManualEntry {
  id: string;
  title: string;
  category: Category;
  access_level: number;
  technical_content: TechnicalContent;
  lore_snippet?: string;
}
