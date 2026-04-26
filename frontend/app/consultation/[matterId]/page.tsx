import { ConsultationView } from "@/components/consultation/ConsultationView";
import { AppShell } from "@/components/shell/AppShell";

export default function ConsultationPage() {
  return (
    <AppShell active="Consultation">
      <ConsultationView />
    </AppShell>
  );
}
