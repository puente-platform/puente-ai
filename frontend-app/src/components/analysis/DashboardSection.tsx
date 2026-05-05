import { ReactNode } from "react";
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

type Props = {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
};

export function DashboardSection({ title, icon: Icon, children }: Props) {
  return (
    <Card className="bg-gradient-card border-gold-subtle">
      <CardContent className="p-4 md:p-5">
        <div className="flex items-center gap-2 mb-3 md:mb-4">
          {Icon && <Icon data-testid="dashboard-section-icon" className="h-3.5 w-3.5 text-muted-foreground" />}
          <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
            {title}
          </p>
        </div>
        {children}
      </CardContent>
    </Card>
  );
}
