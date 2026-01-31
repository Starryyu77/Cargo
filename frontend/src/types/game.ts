
export interface Telemetry {
    co2: number;
    temp: number;
    heart_rate: number;
    pressure: number;
    o2: number;
    battery: number;
    power_draw: number;
    stress: number;
    inventory?: string[]; // Add inventory support
}
