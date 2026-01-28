import React, { useState, useEffect } from 'react';
import { adminService } from '@/services/adminService';
import type { BotConfig } from '@/services/adminService';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Trash2, Save } from 'lucide-react';
import { toast } from 'sonner';

interface DynamicField {
    key: string;
    description: string;
}

const Settings: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [config, setConfig] = useState<BotConfig | null>(null);
    const [systemPrompt, setSystemPrompt] = useState('');
    const [fields, setFields] = useState<DynamicField[]>([]);

    useEffect(() => {
        const loadConfig = async () => {
            try {
                const data = await adminService.fetchConfig();
                setConfig(data);
                setSystemPrompt(data.system_prompt || '');
                const mappedFields = Object.entries(data.voice_settings?.dynamic_fields || {}).map(
                    ([key, description]) => ({ key, description: description as string })
                );
                setFields(mappedFields);
            } catch (error) {
                toast.error('Failed to load configuration');
            } finally {
                setLoading(false);
            }
        };

        loadConfig();
    }, []);

    const addField = () => {
        setFields([...fields, { key: '', description: '' }]);
    };

    const removeField = (index: number) => {
        setFields(fields.filter((_, i) => i !== index));
    };

    const updateField = (index: number, key: 'key' | 'description', value: string) => {
        const newFields = [...fields];
        newFields[index][key] = value;
        setFields(newFields);
    };

    const handleSave = async () => {
        if (!config) return;

        try {
            const dynamicFields: Record<string, string> = {};
            fields.forEach((f) => {
                if (f.key.trim()) {
                    dynamicFields[f.key.trim()] = f.description;
                }
            });

            const updatedConfig: BotConfig = {
                ...config,
                system_prompt: systemPrompt,
                voice_settings: {
                    ...config.voice_settings,
                    dynamic_fields: dynamicFields,
                },
            };

            await adminService.updateConfig(updatedConfig);
            setConfig(updatedConfig);
            toast.success('Configuration saved and reloaded');
        } catch (error) {
            toast.error('Failed to save configuration');
        }
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-[200px] w-full" />
                <Skeleton className="h-[400px] w-full" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-12">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Bot Configuration</h1>
                    <p className="text-muted-foreground">Manage your voice assistant's personality and data collection fields.</p>
                </div>
                <Button onClick={handleSave} size="lg" className="shadow-md">
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>System Prompt</CardTitle>
                    <CardDescription>
                        This instruction set defines how your AI behaves, its tone of voice, and its goals.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Textarea
                        placeholder="You are a helpful AI assistant..."
                        className="min-h-[200px] font-mono text-sm"
                        value={systemPrompt}
                        onChange={(e) => setSystemPrompt(e.target.value)}
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle>Dynamic Tool Discovery</CardTitle>
                        <CardDescription>
                            Define fields the bot should extract from conversation. Changes generate new function schemas.
                        </CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={addField}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Field
                    </Button>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {fields.length === 0 && (
                            <div className="text-center py-8 border-2 border-dashed rounded-lg text-muted-foreground">
                                No dynamic fields defined. Click "Add Field" to start.
                            </div>
                        )}
                        {fields.map((field, index) => (
                            <div key={index} className="flex gap-4 items-start">
                                <div className="flex-1 space-y-2">
                                    <Label className="text-xs uppercase text-muted-foreground">Field Key</Label>
                                    <Input
                                        placeholder="e.g. customer_name"
                                        value={field.key}
                                        onChange={(e) => updateField(index, 'key', e.target.value)}
                                    />
                                </div>
                                <div className="flex-[2] space-y-2">
                                    <Label className="text-xs uppercase text-muted-foreground">Description / Guide</Label>
                                    <Input
                                        placeholder="e.g. Ask for the full name including SURNAME"
                                        value={field.description}
                                        onChange={(e) => updateField(index, 'description', e.target.value)}
                                    />
                                </div>
                                <div className="pt-8">
                                    <Button variant="ghost" size="icon" onClick={() => removeField(index)} className="text-destructive">
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            <div className="flex justify-end">
                <Button onClick={handleSave} size="lg" className="px-8">
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                </Button>
            </div>
        </div>
    );
};

export default Settings;
