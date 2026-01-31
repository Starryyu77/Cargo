import { useState, useCallback } from 'react';

// Mock response logic from survivor_jack.py
const mockResponse = (prompt: string): string => {
  const p = prompt.toLowerCase();
  
  if (p.includes("hummmmm")) return "Whoa... hear that? It's humming. Lights are on! You actually know your stuff, boss.";
  if (p.includes("sparks!") || p.includes("smoking")) return "GAH! *Cough* *Cough* IT BIT ME! The panel is smoking! Did you read the manual upside down?!";
  if (p.includes("jammed into terminal a")) return "Alright, twisting the red one onto the A terminal... Tight. Don't electrocute me.";
  if (p.includes("blue wire is connected to terminal b")) return "Blue one going to B. This wire feels greasy. Done.";
  if (p.includes("cover is off")) return "Got the cover off. Man, it's a rat's nest in here. I see Red, Blue, and a Switch.";
  if (p.includes("standing in front of a gray metal box")) return "I'm freezing here. The box is just staring at me. What do I do?";
  
  return "Uh, say again? It's loud in here and I'm freezing. Just tell me what to stick where.";
};

export const useSurvivorJack = () => {
  const [isTyping, setIsTyping] = useState(false);

  const speak = useCallback(async (userPrompt: string): Promise<string> => {
    setIsTyping(true);
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));
    const response = mockResponse(userPrompt);
    setIsTyping(false);
    return response;
  }, []);

  return {
    speak,
    isTyping
  };
};
