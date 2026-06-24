const diff = `diff --git a/frontend/src/components/Header.tsx b/frontend/src/components/Header.tsx
index 1234567..89abcd 100644
--- a/frontend/src/components/Header.tsx
+++ b/frontend/src/components/Header.tsx
@@ -1,6 +1,7 @@
 import React from 'react';
 import { Button } from './ui/Button';
+import { UserAvatar } from './UserAvatar';
 import { useAuth } from '@/hooks/useAuth';
-import { OldAvatar } from './OldAvatar';
 
 export function Header() {
   const { user, login } = useAuth();
@@ -15,7 +16,11 @@
       <div className="logo">My App</div>
       <nav>
         {user ? (
-          <OldAvatar user={user} />
+          <div className="flex items-center gap-4">
+            <span>Welcome, {user.name}</span>
+            <UserAvatar src={user.avatarUrl} />
+          </div>
         ) : (
           <Button onClick={login}>Login</Button>
         )}
diff --git a/frontend/src/components/UserAvatar.tsx b/frontend/src/components/UserAvatar.tsx
new file mode 100644
index 0000000..abcdef1
--- /dev/null
+++ b/frontend/src/components/UserAvatar.tsx
@@ -0,0 +1,9 @@
+import React from 'react';
+import Image from 'next/image';
+import { cn } from '@/lib/utils';
+
+export function UserAvatar({ src }: { src: string }) {
+  return (
+    <Image src={src || '/default-avatar.png'} alt="User Avatar" width={32} height={32} className={cn("rounded-full")} />
+  );
+}`;
export { diff };