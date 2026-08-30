import { NavMain } from "@/components/nav-main";
import { NavHelp } from "@/components/nav-helps";
import { NavSecondary } from "@/components/nav-secondary";
import { NavUser } from "@/components/nav-user";

import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader } from "@/components/ui/sidebar";

import {
  TerminalSquareIcon,
  Settings2Icon,
  LifeBuoyIcon,
  FrameIcon,
  ShieldCheckIcon,
  FileTextIcon,
  LucideLayoutDashboard,
} from "lucide-react";

import useAuthStore from "@/service/store/authStore";
import { useAuth } from "@/contexts/AuthContext";

import ApiLogo from "@/assets/Api.png";

const data = {
  navMain: [
    {
      title: "DashBoard",
      url: "/dashboard",
      icon: <LucideLayoutDashboard />,
    },
    {
      title: "Projects",
      url: "/project",
      icon: <TerminalSquareIcon />,
      isActive: true,
      items: [
        {
          title: "List",
          url: "/project/list",
        },
        {
          title: "Create",
          url: "/project/create",
        },
      ],
    },
    {
      title: "Settings",
      url: "/settings",
      isActive: true,
      icon: <Settings2Icon />,
      items: [
        {
          title: "Edit Account",
          url: "/settings/account",
        },
        {
          title: "Danger",
          url: "/settings/danger",
        },
      ],
    },
  ],

  navSecondary: [
    {
      title: "Support",
      url: "/support",
      icon: <LifeBuoyIcon />,
    },
    {
      title: "Privacy Policy",
      url: "/policy",
      icon: <ShieldCheckIcon />,
    },
    {
      title: "Terms of Service",
      url: "/terms",
      icon: <FileTextIcon />,
    },
  ],

  help: [
    {
      name: "Documentation V1.0",
      url: "/docs",
      icon: <FrameIcon />,
    },
  ],
};

export function AppSidebar({ ...props }) {
  const user = useAuthStore((state) => state.user);
  const { logout, logoutAll } = useAuth();

  const sidebarUser = {
    name: user?.username || "User",
    email: user?.email || "",
    avatar: user?.avatar || ApiLogo,
  };

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg border bg-background shadow-sm">
            <img src={ApiLogo} alt="Mokvio" className="size-6 object-contain" />
          </div>

          <div className="flex min-w-0 flex-col leading-tight">
            <span className="truncate text-sm font-semibold tracking-tight">Mokvio</span>

            <span className="truncate text-xs text-muted-foreground">DashBoard</span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <NavMain items={data.navMain} />

        <NavHelp helps={data.help} />

        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>

      <SidebarFooter>
        <NavUser user={sidebarUser} onLogout={logout} onLogoutAll={logoutAll} />
      </SidebarFooter>
    </Sidebar>
  );
}
