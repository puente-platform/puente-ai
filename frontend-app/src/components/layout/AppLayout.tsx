import { Outlet } from "react-router-dom";
import AppSidebar from "./AppSidebar";
import TopBar from "./TopBar";
import TrustFooter from "./TrustFooter";
import MobileNav from "./MobileNav";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-gradient-navy">
      <AppSidebar />
      <div className="md:pl-[240px] flex flex-col min-h-screen">
        <TopBar />
        <main className="flex-1 p-4 md:p-6 max-w-[1200px] pb-24 md:pb-6">
          <Outlet />
        </main>
        <TrustFooter />
      </div>
      <MobileNav />
    </div>
  );
}
