import api from '@/lib/api';

export interface BotConfig {
    system_prompt: string;
    voice_settings: {
        provider: string;
        voice_id: string;
        stability: number;
        similarity_boost: number;
        dynamic_fields: Record<string, string>;
    };
    tools_enabled?: string[];
}

export const adminService = {
    fetchConfig: async (): Promise<BotConfig> => {
        const response = await api.get('/config');
        return response.data;
    },

    updateConfig: async (data: BotConfig): Promise<void> => {
        await api.post('/config', data);
    },

    fetchLogs: async (): Promise<any[]> => {
        const response = await api.get('/logs');
        return response.data;
    },
};
