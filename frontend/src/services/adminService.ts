import api from '@/lib/api';

export interface Order {
    id: string;
    customer_name: string;
    phone: string;
    status?: string;
    created_at?: string;
    notes?: string;
}

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

    fetchOrders: async (): Promise<Order[]> => {
        const response = await api.get('/orders');
        return response.data;
    },

    fetchLeads: async (): Promise<any[]> => {
        const response = await api.get('/leads');
        return response.data;
    },
};
