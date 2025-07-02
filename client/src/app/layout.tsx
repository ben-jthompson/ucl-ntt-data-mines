import HeaderWrapper from "../components/HeaderWrapper";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <HeaderWrapper>
          <main>{children}</main>
        </HeaderWrapper>
      </body>
    </html>
  );
}
